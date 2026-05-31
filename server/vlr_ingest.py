"""Fetch pro match results and player stats from VLR (vlr.orlandomm.net + vlr.gg)."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

SERVER_DIR = Path(__file__).resolve().parent
VLR_API = "https://vlr.orlandomm.net/api/v1"
VLR_MATCH_URL = "https://www.vlr.gg/{match_id}/{slug}"
INGESTED_IDS_PATH = SERVER_DIR / "data" / "vlr_ingested_match_ids.json"
REQUEST_DELAY = 0.4

TEAM_ALIASES = {
    "Mega Minors": "NRG",
    "NRG Esports": "NRG",
    "Talon Esports": "TALON",
    "Envy": "ENVY",
}

REGION_SHORT = {
    "AMER": "Americas",
    "EMEA": "EMEA",
    "PAC": "Pacific",
    "PACIFIC": "Pacific",
    "CN": "China",
    "CHINA": "China",
}

PRO_EVENT_PATTERN = re.compile(
    r"^(Valorant Champions|Valorant Masters|VCT \d{4}: (Americas|EMEA|Pacific|China))",
    re.I,
)

PLAYER_STATS_COLUMNS = [
    "Tournament",
    "Stage",
    "Match Type",
    "Player",
    "Teams",
    "Agents",
    "Rounds Played",
    "Rating",
    "Average Combat Score",
    "Kills:Deaths",
    "Kill, Assist, Trade, Survive %",
    "Average Damage Per Round",
    "Kills Per Round",
    "Assists Per Round",
    "First Kills Per Round",
    "First Deaths Per Round",
    "Headshot %",
    "Clutch Success %",
    "Clutches (won/played)",
    "Maximum Kills in a Single Map",
    "Kills",
    "Deaths",
    "Assists",
    "First Kills",
    "First Deaths",
]

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


@dataclass
class VlrMatch:
    match_id: str
    url: str
    tournament: str
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    winner: str
    stage: str = "Main Event"
    match_type: str = "Match"
    player_rows: list[dict[str, Any]] = field(default_factory=list)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "VCT-Match-Predictor/1.0 (dataset sync)"})
    return s


def normalize_team(name: str, canonical: set[str] | None = None) -> str:
    if pd.isna(name):
        return name
    name = TEAM_ALIASES.get(str(name).strip(), str(name).strip())
    if not canonical:
        return name
    if name in canonical:
        return name
    lower = name.lower()
    for team in canonical:
        if team.lower() == lower:
            return team
    for team in canonical:
        if team.lower().replace(" esports", "") == lower.replace(" esports", ""):
            return team
    return name


def normalize_tournament(name: str) -> str:
    name = " ".join(str(name).split())
    m = re.search(
        r"VCT\s*26:\s*(\w+)\s+(Kickoff|Stage\s*\d+)",
        name,
        re.I,
    )
    if m:
        region = REGION_SHORT.get(m.group(1).upper(), m.group(1).title())
        tail = m.group(2)
        if re.search(r"kickoff", tail, re.I):
            return f"VCT 2026: {region} Kickoff"
        stage_num = re.search(r"(\d+)", tail)
        if stage_num:
            return f"VCT 2026: {region} Stage {stage_num.group(1)}"
    return name


def is_pro_event(name: str) -> bool:
    normalized = normalize_tournament(name)
    if "ascension" in normalized.lower():
        return False
    return bool(PRO_EVENT_PATTERN.match(normalized))


def load_ingested_ids() -> set[str]:
    if not INGESTED_IDS_PATH.exists():
        return set()
    try:
        data = json.loads(INGESTED_IDS_PATH.read_text(encoding="utf-8"))
        return set(str(x) for x in data.get("match_ids", []))
    except (json.JSONDecodeError, OSError):
        return set()


def save_ingested_ids(ids: set[str]) -> None:
    INGESTED_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    INGESTED_IDS_PATH.write_text(
        json.dumps({"match_ids": sorted(ids)}, indent=2),
        encoding="utf-8",
    )


def fetch_completed_pro_events(session: requests.Session, max_pages: int = 8) -> list[dict]:
    events: list[dict] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        resp = session.get(f"{VLR_API}/events", params={"page": page, "limit": 50}, timeout=30)
        resp.raise_for_status()
        batch = resp.json().get("data") or []
        if not batch:
            break
        for event in batch:
            eid = str(event.get("id", ""))
            if eid in seen:
                continue
            seen.add(eid)
            if event.get("status") != "completed":
                continue
            if not is_pro_event(event.get("name", "")):
                continue
            events.append(
                {
                    "id": eid,
                    "name": normalize_tournament(event.get("name", "")),
                }
            )
        time.sleep(REQUEST_DELAY)
    return events


def _event_team_ids(session: requests.Session, event_id: str) -> list[str]:
    ids: list[str] = []
    page = 1
    while True:
        resp = session.get(
            f"{VLR_API}/teams",
            params={"event": event_id, "page": page, "limit": 50},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("data") or []
        if not batch:
            break
        ids.extend(str(t["id"]) for t in batch if t.get("id"))
        pagination = payload.get("pagination") or {}
        if not pagination.get("hasNextPage"):
            break
        page += 1
        time.sleep(REQUEST_DELAY)
    return ids


def _collect_event_match_stubs(
    session: requests.Session,
    event_id: str,
    event_name: str,
) -> dict[str, dict]:
    """Return match_id -> stub from team result feeds."""
    target = normalize_tournament(event_name)
    stubs: dict[str, dict] = {}
    team_ids = _event_team_ids(session, event_id)
    for team_id in team_ids:
        resp = session.get(
            f"{VLR_API}/teams/{team_id}",
            params={"event": event_id},
            timeout=30,
        )
        if resp.status_code != 200:
            time.sleep(REQUEST_DELAY)
            continue
        results = (resp.json().get("data") or {}).get("results") or []
        for row in results:
            evt = normalize_tournament((row.get("event") or {}).get("name", ""))
            if evt != target:
                continue
            match = row.get("match") or {}
            mid = str(match.get("id", ""))
            if not mid:
                continue
            teams = row.get("teams") or []
            if len(teams) != 2:
                continue
            stubs[mid] = {
                "match_id": mid,
                "url": match.get("url") or VLR_MATCH_URL.format(match_id=mid, slug="match"),
                "tournament": target,
                "teams": teams,
            }
        time.sleep(REQUEST_DELAY)
    return stubs


def _parse_both(span) -> float | None:
    if not span:
        return None
    el = span.select_one(".mod-both")
    if not el:
        return None
    text = el.get_text(strip=True).replace("%", "")
    try:
        return float(text)
    except ValueError:
        return None


def clean_team_display_name(name: str, canonical: set[str] | None = None) -> str:
    """Strip sponsor prefixes; prefer parenthetical canonical name from VLR."""
    if pd.isna(name):
        return name
    name = str(name).strip()
    paren = re.search(r"\(([^)]+)\)\s*$", name)
    if paren:
        name = paren.group(1).strip()
    return normalize_team(name, canonical)


def _parse_stage_match_type(soup: BeautifulSoup, tournament: str) -> tuple[str, str]:
    stage = "Main Event"
    match_type = "Match"
    header = soup.select_one(".match-header-event")
    if not header:
        return stage, match_type
    text = " ".join(header.get_text(" ", strip=True).split())
    if tournament and tournament in text:
        text = text.replace(tournament, "", 1).strip()
    for sep in ("Playoffs:", "Group Stage:", "Main Event:", "Swiss Stage:"):
        if sep in text:
            stage = sep.replace(":", "").strip()
            rest = text.split(sep, 1)[1].strip()
            if rest:
                match_type = rest
            return stage, match_type
    if text:
        match_type = text
    return stage, match_type


def _parse_match_header(soup: BeautifulSoup, fallback_tournament: str) -> tuple[str, str, str]:
    tournament = normalize_tournament(fallback_tournament)
    stage, match_type = _parse_stage_match_type(soup, tournament)
    return tournament, stage, match_type


def _parse_map_player_rows(
    table,
    tournament: str,
    stage: str,
    match_type: str,
    canonical: set[str],
    tag_map: dict[str, str],
) -> list[dict]:
    rows: list[dict] = []
    for tr in table.select("tbody tr"):
        player_cell = tr.select_one("td.mod-player")
        if not player_cell:
            continue
        ign_el = player_cell.select_one(".text-of")
        tag_el = player_cell.select_one(".ge-text-light")
        if not ign_el:
            continue
        player = ign_el.get_text(strip=True)
        tag = tag_el.get_text(strip=True) if tag_el else ""
        team = tag_map.get(tag) or tag_map.get(tag.upper()) or clean_team_display_name(tag, canonical)
        stat_cells = tr.select("td.mod-stat")
        if len(stat_cells) < 11:
            continue
        rating = _parse_both(stat_cells[0])
        acs = _parse_both(stat_cells[1])
        kills = _parse_both(stat_cells[2])
        deaths = _parse_both(stat_cells[3])
        assists = _parse_both(stat_cells[4])
        adr = _parse_both(stat_cells[7])
        fk = _parse_both(stat_cells[9])
        fd = _parse_both(stat_cells[10])
        if kills is None or deaths is None:
            continue
        kd = kills / deaths if deaths else kills
        agents = ", ".join(
            img.get("title", "") for img in tr.select("td.mod-agents img[title]")
        )
        rows.append(
            {
                "Tournament": tournament,
                "Stage": stage,
                "Match Type": match_type,
                "Player": player,
                "Teams": team,
                "Agents": agents or "unknown",
                "Rounds Played": None,
                "Rating": rating,
                "Average Combat Score": acs,
                "Kills:Deaths": kd,
                "Kill, Assist, Trade, Survive %": None,
                "Average Damage Per Round": adr,
                "Kills Per Round": None,
                "Assists Per Round": None,
                "First Kills Per Round": fk,
                "First Deaths Per Round": fd,
                "Headshot %": _parse_both(stat_cells[8]) if len(stat_cells) > 8 else None,
                "Clutch Success %": None,
                "Clutches (won/played)": None,
                "Maximum Kills in a Single Map": kills,
                "Kills": kills,
                "Deaths": deaths,
                "Assists": assists,
                "First Kills": fk,
                "First Deaths": fd,
            }
        )
    return rows


def _parse_match_teams(soup: BeautifulSoup, stub: dict, canonical: set[str]) -> tuple[str, str, dict[str, str]]:
    """Return team_a, team_b, and tag -> canonical name map."""
    teams = stub["teams"]
    team_a = clean_team_display_name(teams[0].get("name", teams[0].get("tag", "")), canonical)
    team_b = clean_team_display_name(teams[1].get("name", teams[1].get("tag", "")), canonical)
    tag_map: dict[str, str] = {}
    for entry, full in zip(teams, (team_a, team_b)):
        for key in (entry.get("tag"), entry.get("name")):
            if key:
                tag_map[str(key).strip().upper()] = full
                tag_map[str(key).strip()] = full

    vs = soup.select_one(".match-header-vs")
    if vs:
        text = vs.get_text(" ", strip=True)
        m = re.match(
            r"(.+?)\s+final\s+(\d+)\s*:\s*(\d+)\s+vs\.\s+Bo\d+\s+(.+)$",
            text,
            re.I,
        )
        if m:
            team_a = clean_team_display_name(m.group(1).strip(), canonical)
            team_b = clean_team_display_name(m.group(4).strip(), canonical)
            tag_map[team_a.upper()] = team_a
            tag_map[team_b.upper()] = team_b
    return team_a, team_b, tag_map


def scrape_match(
    stub: dict,
    session: requests.Session,
    canonical: set[str],
) -> VlrMatch | None:
    url = stub["url"]
    if not url.startswith("http"):
        url = f"https://www.vlr.gg{url}"

    resp = session.get(url, timeout=45)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    tournament, stage, match_type = _parse_match_header(soup, stub["tournament"])

    teams = stub["teams"]
    team_a, team_b, tag_map = _parse_match_teams(soup, stub, canonical)
    score_a = int(str(teams[0].get("points", "0")).strip() or 0)
    score_b = int(str(teams[1].get("points", "0")).strip() or 0)

    if teams[0].get("won"):
        winner = team_a
    elif teams[1].get("won"):
        winner = team_b
    elif score_a != score_b:
        winner = team_a if score_a > score_b else team_b
    else:
        return None

    player_rows: list[dict] = []
    for table in soup.select("table.wf-table-inset.mod-overview"):
        player_rows.extend(
            _parse_map_player_rows(
                table, tournament, stage, match_type, canonical, tag_map
            )
        )

    return VlrMatch(
        match_id=stub["match_id"],
        url=url,
        tournament=tournament,
        team_a=team_a,
        team_b=team_b,
        score_a=score_a,
        score_b=score_b,
        winner=winner,
        stage=stage,
        match_type=match_type,
        player_rows=player_rows,
    )


def repair_vlr_scores(scores: pd.DataFrame) -> pd.DataFrame:
    """Fix rows ingested with broken tournament/stage/team fields."""
    out = scores.copy()
    region_re = re.compile(
        r"^(Americas|EMEA|Pacific|China)\s+Stage\s+(\d+)\s+(Group Stage|Playoffs|Main Event|Swiss Stage)$"
    )
    for idx, row in out.iterrows():
        if row["Tournament"] != "VCT 2026":
            continue
        m = region_re.match(str(row["Stage"]))
        if m:
            region, num, stage = m.groups()
            out.at[idx, "Tournament"] = f"VCT 2026: {region} Stage {num}"
            out.at[idx, "Stage"] = stage
        for col in ("Team A", "Team B"):
            cleaned = clean_team_display_name(row[col])
            out.at[idx, col] = cleaned
        a, b = out.at[idx, "Team A"], out.at[idx, "Team B"]
        out.at[idx, "Match Name"] = f"{a} vs {b}"
        winner = str(row["Match Result"]).replace(" won", "")
        winner = clean_team_display_name(winner)
        if winner in (a, b):
            out.at[idx, "Match Result"] = f"{winner} won"
    return out


def repair_vlr_player_stats(players: pd.DataFrame) -> pd.DataFrame:
    out = players.copy()
    region_re = re.compile(
        r"^(Americas|EMEA|Pacific|China)\s+Stage\s+(\d+)\s+(Group Stage|Playoffs|Main Event|Swiss Stage)$"
    )
    for idx, row in out.iterrows():
        if row.get("Tournament") != "VCT 2026":
            continue
        m = region_re.match(str(row.get("Stage", "")))
        if m:
            region, num, stage = m.groups()
            out.at[idx, "Tournament"] = f"VCT 2026: {region} Stage {num}"
            out.at[idx, "Stage"] = stage
        out.at[idx, "Teams"] = clean_team_display_name(row.get("Teams"))
    return out


def match_to_score_row(match: VlrMatch) -> dict:
    return {
        "Tournament": match.tournament,
        "Stage": match.stage,
        "Match Type": match.match_type,
        "Match Name": f"{match.team_a} vs {match.team_b}",
        "Team A": match.team_a,
        "Team B": match.team_b,
        "Team A Score": match.score_a,
        "Team B Score": match.score_b,
        "Match Result": f"{match.winner} won",
    }


def score_dedupe_key(row: dict) -> tuple:
    a, b = sorted([row["Team A"], row["Team B"]])
    return (
        row["Tournament"],
        a,
        b,
        int(row["Team A Score"]),
        int(row["Team B Score"]),
    )


def existing_score_keys(scores: pd.DataFrame) -> set[tuple]:
    keys: set[tuple] = set()
    for _, row in scores.iterrows():
        keys.add(
            score_dedupe_key(
                {
                    "Tournament": row["Tournament"],
                    "Team A": row["Team A"],
                    "Team B": row["Team B"],
                    "Team A Score": row["Team A Score"],
                    "Team B Score": row["Team B Score"],
                }
            )
        )
    return keys


def events_missing_from_scores(
    scores: pd.DataFrame,
    events: list[dict],
) -> list[dict]:
    existing = {normalize_tournament(t) for t in scores["Tournament"].astype(str).unique()}
    return [e for e in events if e["name"] not in existing]


def fetch_new_vlr_data(
    scores: pd.DataFrame,
    *,
    event_ids: list[str] | None = None,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, set[str]]:
    """
    Fetch matches from VLR not already present in scores.csv.
    Returns (new_score_rows, new_player_stats_rows, ingested_match_ids).
    """
    session = _session()
    canonical = set(scores["Team A"]).union(scores["Team B"])
    canonical = {normalize_team(t, None) for t in canonical}

    ingested = load_ingested_ids()
    existing_keys = existing_score_keys(scores)

    events = fetch_completed_pro_events(session)
    if event_ids:
        allowed = set(event_ids)
        events = [e for e in events if e["id"] in allowed]
    else:
        events = events_missing_from_scores(scores, events)

    if verbose:
        print(f"VLR: {len(events)} pro event(s) to scan for new matches", flush=True)

    stubs: dict[str, dict] = {}
    for event in events:
        if verbose:
            print(f"  Scanning {event['name']} (id {event['id']})...", flush=True)
        found = _collect_event_match_stubs(session, event["id"], event["name"])
        for mid, stub in found.items():
            if mid not in ingested:
                stubs[mid] = stub
        if verbose:
            print(f"    {len(found)} matches, {len(stubs)} pending after dedupe", flush=True)

    new_scores: list[dict] = []
    new_players: list[dict] = []
    new_ids: set[str] = set()

    for i, (mid, stub) in enumerate(sorted(stubs.items()), start=1):
        if verbose:
            print(f"  Scraping match {i}/{len(stubs)} ({mid})...", flush=True)
        parsed = scrape_match(stub, session, canonical)
        time.sleep(REQUEST_DELAY)
        if not parsed:
            continue
        row = match_to_score_row(parsed)
        key = score_dedupe_key(row)
        if key in existing_keys:
            ingested.add(mid)
            continue
        if not parsed.player_rows:
            if verbose:
                print(f"    Skipped {mid}: no player stats", flush=True)
            continue
        new_scores.append(row)
        new_players.extend(parsed.player_rows)
        new_ids.add(mid)
        existing_keys.add(key)
        ingested.add(mid)
        canonical.update({row["Team A"], row["Team B"]})

    save_ingested_ids(ingested)

    scores_df = pd.DataFrame(new_scores, columns=SCORES_COLUMNS) if new_scores else pd.DataFrame(columns=SCORES_COLUMNS)
    players_df = (
        pd.DataFrame(new_players, columns=PLAYER_STATS_COLUMNS)
        if new_players
        else pd.DataFrame(columns=PLAYER_STATS_COLUMNS)
    )
    return scores_df, players_df, new_ids
