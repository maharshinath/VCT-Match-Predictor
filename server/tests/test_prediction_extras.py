"""Tests for prediction helpers."""

import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

from models.RandomForestPredictor import RandomForestPredictor
from prediction_extras import simulate_series
from vct_config import COMP_POOL_MAPS


def _sample_map_preds():
    return [
        {
            "map": name,
            "team1_win_probability": 55.0,
            "team2_win_probability": 45.0,
            "in_comp_pool": True,
        }
        for name in COMP_POOL_MAPS
    ]


def test_simulate_series_is_deterministic():
    maps = _sample_map_preds()
    first = simulate_series(maps, best_of=3)
    second = simulate_series(maps, best_of=3)
    assert first["team1_series_win_probability"] == second["team1_series_win_probability"]
    assert first["method"] == "exact"


def test_rolling_h2h_from_tracker():
    predictor = RandomForestPredictor()
    rate = predictor.get_winrate_team1("Xi Lai Gaming", "Dragon Ranger Gaming")
    assert 0 <= rate <= 100


def test_team_winrate_uses_recent_window():
    predictor = RandomForestPredictor()
    row = predictor.team_data.loc[predictor.team_data["Team"] == "Xi Lai Gaming"].iloc[0]
    expected = predictor.recent_form["Xi Lai Gaming"]
    # Allow small drift vs CSV snapshot after margin-Elo rebuilds.
    assert row["Winrate"] == pytest.approx(expected, abs=1.5)
