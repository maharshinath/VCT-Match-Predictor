"""Match context flags: LAN, same region, roster stability."""

from __future__ import annotations

import statistics

from tournament_utils import is_international_tournament


def same_region(
    team_a: str,
    team_b: str,
    regions: dict[str, str],
) -> int:
    region_a = regions.get(team_a)
    region_b = regions.get(team_b)
    if not region_a or not region_b:
        return 0
    return int(region_a == region_b)


def infer_is_lan(
    tournament: str | None,
    team_a: str,
    team_b: str,
    regions: dict[str, str],
) -> int:
    if tournament:
        return int(is_international_tournament(tournament))
    region_a = regions.get(team_a)
    region_b = regions.get(team_b)
    if region_a and region_b and region_a != region_b:
        return 1
    return 0


def roster_stability_from_ratings(ratings: list[float]) -> float:
    """Higher = more stable (low variance in recent team rating snapshots)."""
    if len(ratings) < 2:
        return 100.0
    std = statistics.pstdev(ratings)
    return max(0.0, min(100.0, 100.0 - std * 35.0))


def enrich_context_features(
    row: dict,
    *,
    team_a: str,
    team_b: str,
    tournament: str | None,
    regions: dict[str, str],
    stability_a: float,
    stability_b: float,
) -> None:
    row["Is LAN"] = infer_is_lan(tournament, team_a, team_b, regions)
    row["Same Region"] = same_region(team_a, team_b, regions)
    row["Team A Roster Stability"] = stability_a
    row["Team B Roster Stability"] = stability_b
    row["Roster stability delta"] = stability_a - stability_b
