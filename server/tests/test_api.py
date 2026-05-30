"""API smoke tests. Run from server/: python -m pytest tests/ -q"""

import json
import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_teams_list(client):
    r = client.get("/api/teams")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert len(data) >= 50


def test_predict_includes_maps(client):
    r = client.get("/api/predict/Sentinels/LOUD")
    assert r.status_code == 200
    data = r.get_json()
    assert "map_predictions" in data
    assert len(data["map_predictions"]) == 12
    assert "team1_win_probability" in data
    assert "confidence" in data
    assert "series_predictions" in data


def test_meta(client):
    r = client.get("/api/meta")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data["comp_pool_maps"]) == 7

