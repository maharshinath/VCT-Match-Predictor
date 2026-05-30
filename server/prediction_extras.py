"""Confidence labels, key factors, series simulation, recent form."""

from __future__ import annotations

import random
from collections import defaultdict
from pathlib import Path

import pandas as pd

from vct_config import COMP_POOL_MAPS, RECENT_FORM_MATCHES

SERVER_DIR = Path(__file__).resolve().parent
KAGGLE_DIR = SERVER_DIR / "data" / "kaggle"


def confidence_label(team1_prob: float) -> dict:
    """Human-readable confidence from favorite's win %."""
    favorite = max(team1_prob, 100.0 - team1_prob)
    edge = abs(team1_prob - 50.0)
    if favorite >= 65 and edge >= 15:
        level, text = "likely", "Likely"
    elif edge >= 8:
        level, text = "slight", "Slight edge"
    else:
        level, text = "tossup", "Toss-up"
    return {"level": level, "label": text, "favorite_probability": round(favorite, 1)}


def build_key_factors(
    team1: str,
    team2: str,
    favored_team: str,
    feature_row: pd.Series,
    recent_form: dict[str, float],
    agent_diversity: dict[str, float],
) -> list[dict]:
    factor_defs = [
        ("Head-to-head win rate", "Team A Winrate vs B", "Team B Winrate vs A", True, True),
        ("Overall win rate", "Team A Winrate", "Team B Winrate", True, True),
        ("Recent form (last matches)", None, None, True, False),
        ("Agent pool diversity", None, None, True, False),
        ("K/D ratio", "Team A K/D Ratio", "Team B K/D Ratio", True, True),
        ("Average damage", "Team A Average Damage", "Team B Average Damage", True, True),
        ("Average combat score", "Team A Average Combat Score", "Team B Average Combat Score", True, True),
        ("Average first kills", "Team A Average First Kills", "Team B Average First Kills", True, True),
        (
            "Average first deaths per round",
            "Team A Average First Deaths Per Round",
            "Team B Average First Deaths Per Round",
            False,
            True,
        ),
    ]

    def fmt_pct(a: float, b: float) -> str:
        return f"{a:.1f}% vs {b:.1f}%"

    def fmt_num(a: float, b: float, decimals: int = 1) -> str:
        return f"{a:.{decimals}f} vs {b:.{decimals}f}"

    candidates: list[tuple[float, str, str]] = []

    for label, col_a, col_b, higher_better, from_row in factor_defs:
        if from_row and col_a and col_b:
            v1, v2 = float(feature_row[col_a]), float(feature_row[col_b])
            if "win rate" in label.lower():
                detail = fmt_pct(v1, v2)
            elif "Deaths" in label:
                detail = fmt_num(v1, v2, 2) + " per round"
            else:
                detail = fmt_num(v1, v2, 2 if "K/D" in label else 1)
        elif label.startswith("Recent form"):
            v1, v2 = recent_form.get(team1, 50.0), recent_form.get(team2, 50.0)
            detail = fmt_pct(v1, v2)
        else:
            v1, v2 = agent_diversity.get(team1, 0.0), agent_diversity.get(team2, 0.0)
            detail = f"{v1:.0f} agents vs {v2:.0f} agents used"

        if higher_better:
            margin = abs(v1 - v2)
            team1_better = v1 > v2
        else:
            margin = abs(v2 - v1)
            team1_better = v1 < v2

        if margin <= 0:
            continue
        favored_is_team1 = favored_team == team1
        if (favored_is_team1 and team1_better) or (not favored_is_team1 and not team1_better):
            candidates.append((margin, label, detail))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [{"label": label, "detail": detail} for _, label, detail in candidates[:6]]


def compute_recent_form(scores: pd.DataFrame, n: int = RECENT_FORM_MATCHES) -> dict[str, float]:
    team_results: dict[str, list[int]] = defaultdict(list)
    for _, row in scores.iterrows():
        team_a, team_b = row["Team A"], row["Team B"]
        winner = str(row["Match Result"]).replace(" won", "")
        team_results[team_a].append(1 if winner == team_a else 0)
        team_results[team_b].append(1 if winner == team_b else 0)

    out: dict[str, float] = {}
    for team, results in team_results.items():
        recent = results[-n:]
        out[team] = sum(recent) / len(recent) * 100 if recent else 50.0
    return out


def compute_agent_diversity() -> dict[str, float]:
    """Unique agents picked per team across latest Kaggle season data."""
    year_dirs = sorted(KAGGLE_DIR.glob("vct_*"), reverse=True)
    for year_dir in year_dirs:
        path = year_dir / "agents" / "teams_picked_agents.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "Team" not in df.columns or "Agent" not in df.columns:
            continue
        return df.groupby("Team")["Agent"].nunique().to_dict()
    return {}


def sort_map_predictions(map_predictions: list[dict]) -> list[dict]:
    return sorted(map_predictions, key=lambda m: m["map"].lower())


def simulate_series(
    map_predictions: list[dict],
    best_of: int = 3,
    trials: int = 6000,
) -> dict:
    wins_needed = best_of // 2 + 1
    comp_maps = [m for m in map_predictions if m.get("in_comp_pool")] or map_predictions
    if not comp_maps:
        comp_maps = map_predictions

    team1_series = 0
    for _ in range(trials):
        t1, t2 = 0, 0
        used: set[str] = set()
        while t1 < wins_needed and t2 < wins_needed:
            pool = [m for m in comp_maps if m["map"] not in used] or comp_maps
            pick = random.choice(pool)
            used.add(pick["map"])
            p1 = pick["team1_win_probability"] / 100.0
            if random.random() < p1:
                t1 += 1
            else:
                t2 += 1
        if t1 >= wins_needed:
            team1_series += 1

    p1 = round(team1_series / trials * 100, 1)
    return {
        "format": f"Bo{best_of}",
        "team1_series_win_probability": p1,
        "team2_series_win_probability": round(100.0 - p1, 1),
        "maps_considered": [m["map"] for m in comp_maps],
        "simulation_trials": trials,
    }
