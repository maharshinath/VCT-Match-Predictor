"""Shared match-winner model training utilities."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split

BASE_FEATURE_COLS = [
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

DELTA_FEATURE_SPECS = [
    ("H2H delta", "Team A Winrate vs B", "Team B Winrate vs A"),
    ("Winrate delta", "Team A Winrate", "Team B Winrate"),
    ("K/D delta", "Team A K/D Ratio", "Team B K/D Ratio"),
    ("Damage delta", "Team A Average Damage", "Team B Average Damage"),
    ("ACS delta", "Team A Average Combat Score", "Team B Average Combat Score"),
    ("First kills delta", "Team A Average First Kills", "Team B Average First Kills"),
    ("First deaths delta", "Team A Average First Deaths Per Round", "Team B Average First Deaths Per Round"),
]

ENGINEERED_FEATURE_COLS = [name for name, _, _ in DELTA_FEATURE_SPECS]
FEATURE_COLS = BASE_FEATURE_COLS + ENGINEERED_FEATURE_COLS

RF_PARAM_DISTRIBUTION = {
    "n_estimators": [200, 300, 400, 500],
    "max_depth": [10, 14, 18, 22, None],
    "min_samples_leaf": [1, 2, 4, 6],
    "min_samples_split": [2, 4, 8],
    "max_features": ["sqrt", "log2", 0.6],
    "class_weight": ["balanced", "balanced_subsample", None],
}


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for name, col_a, col_b in DELTA_FEATURE_SPECS:
        out[name] = pd.to_numeric(out[col_a], errors="coerce") - pd.to_numeric(
            out[col_b], errors="coerce"
        )
    return out


def _swap_team_columns(df: pd.DataFrame) -> pd.DataFrame:
    swapped = df.copy()
    team_a_cols = [c for c in BASE_FEATURE_COLS if c.startswith("Team A")]
    team_b_cols = [c for c in BASE_FEATURE_COLS if c.startswith("Team B")]
    for a_col, b_col in zip(team_a_cols, team_b_cols):
        swapped[a_col] = df[b_col]
        swapped[b_col] = df[a_col]
    return swapped


def create_order_invariant_data(df: pd.DataFrame) -> pd.DataFrame:
    base = df[BASE_FEATURE_COLS + ["Team A Win"]].copy()
    original = add_engineered_features(base)
    swapped_base = _swap_team_columns(base)
    swapped_base["Team A Win"] = 1 - base["Team A Win"].astype(int)
    swapped = add_engineered_features(swapped_base)
    return pd.concat([original, swapped], ignore_index=True)


def load_model_bundle(path) -> tuple[RandomForestClassifier, list[str]]:
    import joblib

    loaded = joblib.load(path)
    if isinstance(loaded, dict) and "model" in loaded:
        return loaded["model"], list(loaded.get("feature_cols", FEATURE_COLS))
    return loaded, FEATURE_COLS


def save_model_bundle(path, model: RandomForestClassifier, feature_cols: list[str] | None = None) -> None:
    import joblib

    joblib.dump(
        {
            "model": model,
            "feature_cols": feature_cols or FEATURE_COLS,
            "version": 2,
        },
        path,
    )


def train_match_model(
    matches: pd.DataFrame,
    *,
    tune: bool = True,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[RandomForestClassifier, dict]:
    augmented = create_order_invariant_data(matches)
    x = augmented[FEATURE_COLS]
    y = augmented["Team A Win"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    if tune:
        search = RandomizedSearchCV(
            RandomForestClassifier(random_state=random_state, n_jobs=-1),
            param_distributions=RF_PARAM_DISTRIBUTION,
            n_iter=24,
            cv=3,
            scoring="accuracy",
            random_state=random_state,
            n_jobs=-1,
            verbose=1,
        )
        search.fit(x_train, y_train)
        model = search.best_estimator_
        best_params = search.best_params_
    else:
        model = RandomForestClassifier(
            n_estimators=400,
            max_depth=16,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        )
        model.fit(x_train, y_train)
        best_params = model.get_params()

    train_acc = model.score(x_train, y_train)
    test_acc = model.score(x_test, y_test)

    report = {
        "train_accuracy": round(train_acc * 100, 1),
        "test_accuracy": round(test_acc * 100, 1),
        "best_params": {k: v for k, v in best_params.items() if k in RF_PARAM_DISTRIBUTION},
        "feature_count": len(FEATURE_COLS),
        "training_rows": len(matches),
        "augmented_rows": len(augmented),
    }
    return model, report
