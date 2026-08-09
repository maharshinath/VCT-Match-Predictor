"""Competitive map-pool strength features for the match winner model."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from vct_config import COMP_POOL_MAPS, MAP_DIFF_BOTTOM_N, MAP_DIFF_MIN_PLAYED, MAP_DIFF_TOP_N

SERVER_DIR = Path(__file__).resolve().parent
MAP_STATS_PATH = SERVER_DIR / "csv" / "map_team_stats.csv"


def load_map_team_lookup() -> dict[tuple[str, str], dict]:
    if not MAP_STATS_PATH.exists():
        return {}
    df = pd.read_csv(MAP_STATS_PATH)
    lookup: dict[tuple[str, str], dict] = {}
    for _, row in df.iterrows():
        lookup[(str(row["Team"]), str(row["Map"]))] = {
            "wins": int(row["Wins"]),
            "played": int(row["Played"]),
            "winrate": float(row["Winrate"]),
        }
    return lookup


def _map_rates(team: str, lookup: dict[tuple[str, str], dict]) -> list[float]:
    rates: list[float] = []
    for map_name in COMP_POOL_MAPS:
        entry = lookup.get((team, map_name))
        if not entry or entry["played"] < MAP_DIFF_MIN_PLAYED:
            continue
        rates.append((entry["wins"] + 1) / (entry["played"] + 2))
    return rates


def comp_pool_map_strength(team: str, lookup: dict[tuple[str, str], dict]) -> float:
    """Weighted average map win rate on the current competitive pool."""
    total_weight = 0.0
    weighted_rate = 0.0
    for map_name in COMP_POOL_MAPS:
        entry = lookup.get((team, map_name))
        if not entry or entry["played"] == 0:
            continue
        weight = min(entry["played"], 20)
        rate = (entry["wins"] + 1) / (entry["played"] + 2)
        weighted_rate += rate * weight
        total_weight += weight
    if total_weight == 0:
        return 50.0
    return weighted_rate / total_weight * 100


def comp_pool_map_differential(team: str, lookup: dict[tuple[str, str], dict]) -> float:
    """Top-N pool map WR minus bottom-N (veto-ish strength), as percentage points."""
    rates = sorted(_map_rates(team, lookup), reverse=True)
    if len(rates) < MAP_DIFF_TOP_N + MAP_DIFF_BOTTOM_N:
        return 0.0
    top = sum(rates[:MAP_DIFF_TOP_N]) / MAP_DIFF_TOP_N
    bottom = sum(rates[-MAP_DIFF_BOTTOM_N:]) / MAP_DIFF_BOTTOM_N
    return (top - bottom) * 100


def enrich_map_features(
    row: dict,
    team_a: str,
    team_b: str,
    lookup: dict[tuple[str, str], dict],
) -> None:
    strength_a = comp_pool_map_strength(team_a, lookup)
    strength_b = comp_pool_map_strength(team_b, lookup)
    diff_a = comp_pool_map_differential(team_a, lookup)
    diff_b = comp_pool_map_differential(team_b, lookup)
    row["Team A Map Pool Strength"] = strength_a
    row["Team B Map Pool Strength"] = strength_b
    row["Map pool strength delta"] = strength_a - strength_b
    row["Team A Map Pool Differential"] = diff_a
    row["Team B Map Pool Differential"] = diff_b
    row["Map pool differential delta"] = diff_a - diff_b
