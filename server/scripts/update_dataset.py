"""
Download (optional) and rebuild VCT CSVs + Random Forest model from Kaggle raw data.

Usage (from server/):
  python scripts/update_dataset.py
  python scripts/update_dataset.py --download   # fetch latest Kaggle zip first
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

SERVER_DIR = Path(__file__).resolve().parents[1]
CSV_DIR = SERVER_DIR / "csv"
MODEL_DIR = SERVER_DIR / "models"
KAGGLE_DIR = SERVER_DIR / "data" / "kaggle"
RAW_DIR = SERVER_DIR / "data" / "raw"

FEATURE_COLS = [
    "Team A Winrate vs B",
    "Team A Winrate",
    "Team A K/D Ratio",
    "Team A Average Damage",
    "Team A Average Combat Score",
    "Team A Average First Kills",
    "Team A Average First Deaths Per Round",
    "Team B Winrate vs A",
    "Team B Winrate",
    "Team B K/D Ratio",
    "Team B Average Damage",
    "Team B Average Combat Score",
    "Team B Average First Kills",
    "Team B Average First Deaths Per Round",
]

TEAM_ALIASES = {
    "Mega Minors": "NRG",
    "NRG Esports": "NRG",
}

# Showmatch / all-star teams to drop from the dropdown
EXCLUDED_TEAMS = {
    "Team Alpha",
    "Team Omega",
    "Team EMEA",
    "Team France",
    "Team International",
    "Team Thailand",
    "Team World",
    "Glory Once Again",
    "Pure Aim",
    "Precise Defeat",
}

PRO_TOURNAMENT_PATTERN = r"Valorant Champions|Valorant Masters|^VCT \d{4}:"
DEFAULT_MIN_YEAR = 2021

SCORES_COLUMNS = [
    "Tournament",
    "Stage",
    "Match Type",
    "Match Name",
    "Team A",
    "Team B",
    "Team A Score",
    "Team B Score",
    "Match Result",
]


def download_kaggle_dataset() -> None:
    KAGGLE_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "kaggle",
            "datasets",
            "download",
            "-d",
            "ryanluong1/valorant-champion-tour-2021-2023-data",
            "-p",
            str(KAGGLE_DIR),
            "--unzip",
        ],
        check=True,
    )


def find_year_dirs(base: Path, min_year: int | None = None) -> list[Path]:
    if not base.exists():
        return []
    dirs = sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("vct_"))
    if min_year is not None:
        dirs = [p for p in dirs if int(p.name.split("_")[1]) >= min_year]
    return dirs


def load_concat_csv(year_dirs: list[Path], *parts: str) -> pd.DataFrame:
    frames = []
    for year_dir in year_dirs:
        path = year_dir.joinpath(*parts)
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        raise FileNotFoundError(f"No files found for {'/'.join(parts)} under {year_dirs[0].parent}")
    combined = pd.concat(frames, ignore_index=True)
    return combined.drop_duplicates()


def normalize_team(name: str) -> str:
    if pd.isna(name):
        return name
    name = str(name).strip()
    return TEAM_ALIASES.get(name, name)


def filter_pro_matches(df: pd.DataFrame) -> pd.DataFrame:
    mask = df["Tournament"].str.contains(PRO_TOURNAMENT_PATTERN, regex=True)
    out = df.loc[mask].copy()
    for col in ("Team A", "Team B"):
        out = out[~out[col].isin(EXCLUDED_TEAMS)]
    return out


def normalize_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = filter_pro_matches(df.copy())
    for col in ("Team A", "Team B"):
        out[col] = out[col].map(normalize_team)

    def fix_result(row):
        result = str(row["Match Result"])
        for alias, canonical in TEAM_ALIASES.items():
            if result == f"{alias} won":
                return f"{canonical} won"
        return result

    out["Match Result"] = out.apply(fix_result, axis=1)
    out["Match Name"] = out["Team A"] + " vs " + out["Team B"]
    return out[SCORES_COLUMNS]


def build_h2h_lookup(scores: pd.DataFrame) -> dict[tuple[str, str], tuple[float, float]]:
    """Map (team_a, team_b) -> (team_a h2h %, team_b h2h %)."""
    lookup: dict[tuple[str, str], tuple[float, float]] = {}
    pair_df = scores.copy()
    pair_df["pair"] = pair_df.apply(
        lambda r: tuple(sorted((r["Team A"], r["Team B"]))), axis=1
    )
    for (team1, team2), group in pair_df.groupby("pair", sort=False):
        results = group["Match Result"].dropna().tolist()
        if not results:
            lookup[(team1, team2)] = (0.0, 0.0)
            lookup[(team2, team1)] = (0.0, 0.0)
            continue
        wins1 = sum(1 for r in results if r == f"{team1} won")
        rate1 = wins1 / len(results) * 100
        rate2 = 100 - rate1
        lookup[(team1, team2)] = (rate1, rate2)
        lookup[(team2, team1)] = (rate2, rate1)
    return lookup


def get_team_winrate(scores: pd.DataFrame, team: str) -> float:
    mask = scores["Match Name"].str.contains(team, regex=False)
    filtered = scores.loc[mask]
    total = len(filtered)
    if total == 0:
        return 0.0
    wins = len(filtered[filtered["Match Result"].str.contains(team, regex=False)])
    return wins / total * 100


def aggregate_player_stats(player_stats: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        player_stats.groupby("Teams")
        .agg(
            {
                "Kills:Deaths": "mean",
                "Average Damage Per Round": "mean",
                "Average Combat Score": "mean",
                "First Kills": "mean",
                "First Deaths Per Round": "mean",
            }
        )
        .reset_index()
        .rename(
            columns={
                "Teams": "Team",
                "Kills:Deaths": "K/D Ratio",
                "Average Damage Per Round": "Average Damage",
                "Average Combat Score": "Average Combat Score",
                "First Kills": "Average First Kills",
                "First Deaths Per Round": "Average First Deaths Per Round",
            }
        )
    )
    return grouped


def get_average_player_stats(player_stats: pd.DataFrame, team: str) -> dict | None:
    filtered = player_stats[player_stats["Teams"] == team]
    if filtered.empty:
        return None
    return {
        "K/D Ratio": filtered["Kills:Deaths"].mean(),
        "Average Damage": filtered["Average Damage Per Round"].mean(),
        "Average Combat Score": filtered["Average Combat Score"].mean(),
        "Average First Kills": filtered["First Kills"].mean(),
        "Average First Deaths Per Round": filtered["First Deaths Per Round"].mean(),
    }


def slugify_team(team: str) -> str:
    slug = team.lower().replace(".", "").replace("'", "")
    slug = slug.replace(" ", "-")
    return slug


def load_existing_logo_map() -> dict[str, str]:
    path = CSV_DIR / "team_data.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    logo_map = {}
    for team, image_path in zip(df["Team"], df["Image Path"]):
        if isinstance(image_path, str) and image_path.startswith("/static/"):
            logo_map[team] = image_path
    return logo_map


def build_team_winrates(scores: pd.DataFrame) -> dict[str, float]:
    wins: dict[str, int] = {}
    played: dict[str, int] = {}
    for _, row in scores.iterrows():
        for team in (row["Team A"], row["Team B"]):
            played[team] = played.get(team, 0) + 1
        winner = str(row["Match Result"]).replace(" won", "")
        wins[winner] = wins.get(winner, 0) + 1
    return {
        team: (wins.get(team, 0) / count * 100) if count else 0.0
        for team, count in played.items()
    }


def active_teams(scores: pd.DataFrame) -> set[str]:
    return set(scores["Team A"]) | set(scores["Team B"])


def build_team_data(scores: pd.DataFrame, player_stats: pd.DataFrame) -> pd.DataFrame:
    player_stats = player_stats.copy()
    player_stats["Teams"] = player_stats["Teams"].map(normalize_team)
    teams = active_teams(scores)

    logo_map = load_existing_logo_map()
    stat_rows = aggregate_player_stats(player_stats)
    stat_rows = stat_rows[stat_rows["Team"].isin(teams)].copy()
    winrates = build_team_winrates(scores)

    stat_rows["Winrate"] = stat_rows["Team"].map(winrates).fillna(0).round(4)
    stat_rows["Image Path"] = stat_rows["Team"].map(
        lambda t: logo_map.get(t) or f"/static/logos/{slugify_team(t)}-logo.png"
    )
    stat_rows = stat_rows.sort_values("Team").reset_index(drop=True)
    stat_rows["id"] = range(1, len(stat_rows) + 1)
    return stat_rows


def build_team_stats_cache(
    player_stats: pd.DataFrame, teams: set[str]
) -> dict[str, dict]:
    agg = aggregate_player_stats(player_stats)
    agg = agg[agg["Team"].isin(teams)]
    return {
        row["Team"]: {
            "K/D Ratio": row["K/D Ratio"],
            "Average Damage": row["Average Damage"],
            "Average Combat Score": row["Average Combat Score"],
            "Average First Kills": row["Average First Kills"],
            "Average First Deaths Per Round": row["Average First Deaths Per Round"],
        }
        for _, row in agg.iterrows()
    }


def build_match_features(
    scores: pd.DataFrame,
    player_stats: pd.DataFrame,
    h2h_lookup: dict[tuple[str, str], tuple[float, float]],
    team_stats: dict[str, dict],
) -> pd.DataFrame:
    winrate_cache = build_team_winrates(scores)
    records = []
    for _, row in scores.iterrows():
        team_a = row["Team A"]
        team_b = row["Team B"]
        stats_a = team_stats.get(team_a)
        stats_b = team_stats.get(team_b)
        if not stats_a or not stats_b:
            continue

        h2h_a, h2h_b = h2h_lookup.get((team_a, team_b), (0.0, 0.0))

        records.append(
            {
                "Tournament": row["Tournament"],
                "Stage": row["Stage"],
                "Match Type": row["Match Type"],
                "Team A": team_a,
                "Team B": team_b,
                "Team A Winrate vs B": h2h_a,
                "Team A Winrate": winrate_cache[team_a],
                **{f"Team A {k}": v for k, v in stats_a.items()},
                "Team B Winrate vs A": h2h_b,
                "Team B Winrate": winrate_cache[team_b],
                **{f"Team B {k}": v for k, v in stats_b.items()},
                "Team A Win": int(str(row["Match Result"]) == f"{team_a} won"),
            }
        )
    return pd.DataFrame(records)


def create_order_invariant_data(df: pd.DataFrame) -> pd.DataFrame:
    original = df.copy()
    swapped = df.copy()
    team_a_cols = [c for c in FEATURE_COLS if "Team A" in c]
    team_b_cols = [c for c in FEATURE_COLS if "Team B" in c]
    for a_col, b_col in zip(team_a_cols, team_b_cols):
        swapped[a_col] = df[b_col]
        swapped[b_col] = df[a_col]
    swapped["Team A Win"] = 1 - df["Team A Win"]
    return pd.concat([original, swapped], ignore_index=True)


def train_model(matches: pd.DataFrame) -> RandomForestClassifier:
    augmented = create_order_invariant_data(matches)
    x = augmented[FEATURE_COLS]
    y = augmented["Team A Win"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(x_train, y_train)
    accuracy = model.score(x_test, y_test)
    print(f"Model test accuracy: {accuracy:.1%}")
    return model


def main(download: bool, min_year: int) -> None:
    if download:
        print("Downloading Kaggle dataset...")
        download_kaggle_dataset()

    year_dirs = find_year_dirs(KAGGLE_DIR, min_year=min_year)
    if not year_dirs:
        year_dirs = find_year_dirs(RAW_DIR, min_year=min_year)
    if not year_dirs:
        raise SystemExit(
            "No vct_* data folders found. Run with --download or place raw data under server/data/kaggle/"
        )

    print(f"Using {len(year_dirs)} season folders: {[p.name for p in year_dirs]}", flush=True)

    print("Loading match results...", flush=True)
    scores = normalize_scores(
        load_concat_csv(year_dirs, "matches", "scores.csv")
    )
    print("Loading player stats...", flush=True)
    player_stats = load_concat_csv(year_dirs, "players_stats", "players_stats.csv")

    player_stats["Teams"] = player_stats["Teams"].map(normalize_team)
    teams = active_teams(scores)

    print("Building team_data.csv...", flush=True)
    team_data = build_team_data(scores, player_stats)
    print("Computing head-to-head rates...", flush=True)
    h2h_lookup = build_h2h_lookup(scores)
    team_stats_cache = build_team_stats_cache(player_stats, teams)
    print("Building filtered_matches.csv...", flush=True)
    filtered_matches = build_match_features(
        scores, player_stats, h2h_lookup, team_stats_cache
    )
    print("Training model...", flush=True)

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    scores.to_csv(CSV_DIR / "scores.csv", index=False)
    team_data.to_csv(CSV_DIR / "team_data.csv", index=False)
    filtered_matches.to_csv(CSV_DIR / "filtered_matches.csv", index=False)

    model = train_model(filtered_matches)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "rf.pkl")

    print(f"scores.csv: {len(scores)} matches")
    print(f"team_data.csv: {len(team_data)} teams")
    print(f"filtered_matches.csv: {len(filtered_matches)} training rows")
    print(f"Saved model to {MODEL_DIR / 'rf.pkl'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild VCT dataset and model")
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download latest data from Kaggle before processing",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        default=DEFAULT_MIN_YEAR,
        help=f"Only include seasons from this year onward (default: {DEFAULT_MIN_YEAR})",
    )
    parser.add_argument(
        "--all-years",
        action="store_true",
        help="Include all seasons (2021+) including Challengers data",
    )
    args = parser.parse_args()
    os.chdir(SERVER_DIR)
    min_year = None if args.all_years else args.min_year
    main(download=args.download, min_year=min_year or 2021)
