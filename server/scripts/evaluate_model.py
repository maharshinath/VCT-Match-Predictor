"""
Evaluate model with random split and time-ordered (by row index) split.
Writes metrics to server/data/model_metrics.json

Usage (from server/):
  python scripts/evaluate_model.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split

SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

from model_training import (  # noqa: E402
    FEATURE_COLS,
    RF_PARAM_DISTRIBUTION,
    create_order_invariant_data,
    load_model_bundle,
)

METRICS_PATH = SERVER_DIR / "data" / "model_metrics.json"


def _fit_eval_model(train_x, train_y) -> RandomForestClassifier:
    search = RandomizedSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        param_distributions=RF_PARAM_DISTRIBUTION,
        n_iter=12,
        cv=3,
        scoring="accuracy",
        random_state=42,
        n_jobs=-1,
    )
    search.fit(train_x, train_y)
    return search.best_estimator_


def evaluate_random_split(df: pd.DataFrame, test_size: float = 0.2) -> float:
    augmented = create_order_invariant_data(df)
    x = augmented[FEATURE_COLS]
    y = augmented["Team A Win"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42, stratify=y
    )
    model = _fit_eval_model(x_train, y_train)
    pred = model.predict(x_test)
    return accuracy_score(y_test, pred)


def evaluate_time_split(df: pd.DataFrame, test_frac: float = 0.2) -> float:
    augmented = create_order_invariant_data(df)
    split = int(len(augmented) * (1 - test_frac))
    train = augmented.iloc[:split]
    test = augmented.iloc[split:]
    model = _fit_eval_model(train[FEATURE_COLS], train["Team A Win"].astype(int))
    pred = model.predict(test[FEATURE_COLS])
    return accuracy_score(test["Team A Win"].astype(int), pred)


def main() -> None:
    matches_path = SERVER_DIR / "csv" / "filtered_matches.csv"
    df = pd.read_csv(matches_path)
    deployed, feature_cols = load_model_bundle(SERVER_DIR / "models" / "rf.pkl")

    random_acc = evaluate_random_split(df)
    time_acc = evaluate_time_split(df)

    augmented = create_order_invariant_data(df)
    split = int(len(augmented) * 0.8)
    holdout = augmented.iloc[split:]
    deployed_acc = accuracy_score(
        holdout["Team A Win"].astype(int),
        deployed.predict(holdout[feature_cols]),
    )

    metrics = {
        "random_split_accuracy": round(random_acc * 100, 1),
        "time_ordered_split_accuracy": round(time_acc * 100, 1),
        "deployed_model_holdout_accuracy": round(deployed_acc * 100, 1),
        "feature_count": len(feature_cols),
        "note": "Time-ordered split is a better proxy for real forecasting than random split.",
    }
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
