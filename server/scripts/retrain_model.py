"""
Retrain model from existing scores.csv without fetching new VLR data.

Usage (from server/):
  python scripts/retrain_model.py
  python scripts/retrain_model.py --no-tune
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))
sys.path.insert(0, str(SERVER_DIR / "scripts"))

from update_dataset import (  # noqa: E402
    CSV_DIR,
    DEFAULT_MIN_YEAR,
    load_merged_player_stats,
    rebuild_pipeline,
)


def main(tune: bool, min_year: int) -> None:
    scores_path = CSV_DIR / "scores.csv"
    if not scores_path.exists():
        raise SystemExit("scores.csv not found. Run sync_vlr_data.py or update_dataset.py first.")

    scores = pd.read_csv(scores_path)
    player_stats = load_merged_player_stats(min_year=min_year)
    print(f"Retraining on {len(scores)} matches...", flush=True)
    rebuild_pipeline(scores, player_stats, tune=tune)

    print("Running evaluate_model.py...", flush=True)
    subprocess.run(
        [sys.executable, "scripts/evaluate_model.py"],
        cwd=SERVER_DIR,
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain model from existing scores.csv")
    parser.add_argument("--no-tune", action="store_true", help="Skip hyperparameter search")
    parser.add_argument("--min-year", type=int, default=DEFAULT_MIN_YEAR)
    args = parser.parse_args()
    os.chdir(SERVER_DIR)
    main(tune=not args.no_tune, min_year=args.min_year)
