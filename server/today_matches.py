"""Upcoming (and live) VCT 2026 matches from VLR.gg for the homepage."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from vlr_ingest import VLR_API, _get_with_retry, clean_team_display_name

_CACHE: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 90.0
_TIMEOUT = 15
_TARGET_YEAR = 2026


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }
    )
    return s


def _is_vct_2026(tournament: str | None) -> bool:
    t = (tournament or "").upper()
    if "VCT" not in t and "CHAMPIONS" not in t and "MASTERS" not in t:
        return False
    return str(_TARGET_YEAR) in t or "2026" in t


def _parse_utc(match: dict) -> datetime | None:
    raw = match.get("utc") or match.get("utcDate")
    if raw:
        try:
            if isinstance(raw, (int, float)):
                return datetime.fromtimestamp(raw, tz=timezone.utc)
            text = str(raw).replace("Z", "+00:00")
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass
    ts = match.get("timestamp")
    if ts:
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except (TypeError, ValueError):
            return None
    return None


def _team_blob(raw: dict) -> dict[str, Any]:
    name = clean_team_display_name(str(raw.get("name") or ""))
    score = raw.get("score")
    score_s = "" if score is None else str(score).strip()
    return {
        "name": name,
        "score": score_s if score_s not in ("", "None") else None,
        "won": bool(raw["won"]) if raw.get("won") is not None else None,
        "logo": raw.get("logo"),
        "id": str(raw.get("id") or "") or None,
    }


def _normalize(match: dict) -> dict[str, Any] | None:
    teams = match.get("teams") or []
    if len(teams) < 2:
        return None
    t1, t2 = _team_blob(teams[0]), _team_blob(teams[1])
    if not t1["name"] or not t2["name"]:
        return None
    if t1["name"].upper() == "TBD" or t2["name"].upper() == "TBD":
        return None
    tournament = str(match.get("tournament") or "")
    if not _is_vct_2026(tournament):
        return None
    status = str(match.get("status") or "").strip() or "Upcoming"
    status_u = status.upper()
    if status_u == "LIVE":
        bucket = "live"
    elif status_u in ("COMPLETED", "COMPLETE", "FINISHED"):
        return None
    else:
        bucket = "upcoming"
    mid = str(match.get("id") or "")
    utc = _parse_utc(match)
    # Drop completed spill / past scheduled if clearly completed status
    if utc and utc.year != _TARGET_YEAR and "2026" not in tournament:
        return None
    return {
        "id": mid,
        "team1": t1,
        "team2": t2,
        "status": status,
        "bucket": bucket,
        "event": match.get("event"),
        "tournament": tournament,
        "utc": utc.isoformat() if utc else None,
        "url": f"https://www.vlr.gg/{mid}" if mid else None,
        "source": "matches",
    }


def _fetch_api_list(session: requests.Session, path: str, params: dict | None = None) -> list[dict]:
    try:
        resp = _get_with_retry(
            session,
            f"{VLR_API}/{path}",
            params=params or {},
            timeout=_TIMEOUT,
            retries=2,
        )
        if resp is None or resp.status_code != 200:
            return []
        payload = resp.json()
        data = payload.get("data") if isinstance(payload, dict) else payload
        return data if isinstance(data, list) else []
    except Exception:
        return []


def fetch_upcoming_matches() -> dict[str, Any]:
    """Live + upcoming VCT 2026 matches (no date='today' filter, no results)."""
    cache_key = "upcoming_vct_2026"
    hit = _CACHE.get(cache_key)
    if hit and time.time() - hit[0] < _CACHE_TTL:
        return hit[1]

    session = _session()
    raw = _fetch_api_list(session, "matches")
    if not raw:
        raw = _fetch_api_list(session, "matches", {"status": "upcoming"})

    by_id: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        row = _normalize(item)
        if not row:
            continue
        key = row["id"] or f"{row['team1']['name']}::{row['team2']['name']}::{row.get('utc')}"
        by_id[key] = row

    matches = list(by_id.values())

    def sort_key(m: dict) -> tuple:
        order = 0 if m["bucket"] == "live" else 1
        return (order, m.get("utc") or "9999", m.get("tournament") or "")

    matches.sort(key=sort_key)

    payload = {
        "year": _TARGET_YEAR,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(matches),
        "matches": matches,
    }
    _CACHE[cache_key] = (time.time(), payload)
    return payload


# Back-compat alias for older imports / routes
def fetch_today_matches(**_kwargs) -> dict[str, Any]:
    return fetch_upcoming_matches()
