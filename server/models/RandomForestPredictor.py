import os
import sys

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(BASE_DIR, "..")
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

from model_training import add_engineered_features, load_model_bundle
from map_predictions import MapPredictor
from prediction_extras import (
    build_key_factors,
    compute_agent_diversity,
    compute_recent_form,
    confidence_label,
    simulate_series,
    sort_map_predictions,
)


class RandomForestPredictor:
    def __init__(self):
        model_path = os.path.join(BASE_DIR, "rf.pkl")
        self.rf_model, self.feature_cols = load_model_bundle(model_path)
        self.team_data = pd.read_csv(os.path.join(BASE_DIR, "../csv/team_data.csv"))
        self.match_data = pd.read_csv(os.path.join(BASE_DIR, "../csv/scores.csv"))
        self.map_predictor = MapPredictor()
        self.recent_form = compute_recent_form(self.match_data)
        self.agent_diversity = compute_agent_diversity()

    def get_past_matches(self, team1, team2):
        match_data = self.match_data.dropna()
        filtered_df = match_data[
            (match_data["Match Name"] == team1 + " vs " + team2)
            | (match_data["Match Name"] == team2 + " vs " + team1)
        ]
        matches = set()
        for i in range(len(filtered_df) - 1, -1, -1):
            matches.add(filtered_df.iloc[i]["Match Result"])
        return matches

    def get_winrate_team1(self, team1, team2):
        match_set = self.get_past_matches(team1, team2)
        if len(match_set) == 0:
            return None
        wins = sum(1 for match in match_set if match == (team1 + " won"))
        return wins / len(match_set) * 100

    def build_pred_df(self, teama, teamb):
        a_data = self.team_data.loc[self.team_data["Team"] == teama]
        b_data = self.team_data.loc[self.team_data["Team"] == teamb]

        if a_data.empty:
            raise ValueError(f"Team '{teama}' not found in team data")
        if b_data.empty:
            raise ValueError(f"Team '{teamb}' not found in team data")

        a_row = a_data.iloc[0]
        b_row = b_data.iloc[0]

        winrate_team1 = self.get_winrate_team1(teama, teamb)
        if winrate_team1 is None:
            winrate_team1 = 0
            winrate_team2 = 0
        else:
            winrate_team2 = 100 - winrate_team1

        pred_df = {
            "Team A Winrate vs B": [winrate_team1],
            "Team A Winrate": [a_row["Winrate"]],
            "Team A K/D Ratio": [a_row["K/D Ratio"]],
            "Team A Average Damage": [a_row["Average Damage"]],
            "Team A Average Combat Score": [a_row["Average Combat Score"]],
            "Team A Average First Kills": [a_row["Average First Kills"]],
            "Team A Average First Deaths Per Round": [a_row["Average First Deaths Per Round"]],
            "Team B Winrate vs A": [winrate_team2],
            "Team B Winrate": [b_row["Winrate"]],
            "Team B K/D Ratio": [b_row["K/D Ratio"]],
            "Team B Average Damage": [b_row["Average Damage"]],
            "Team B Average Combat Score": [b_row["Average Combat Score"]],
            "Team B Average First Kills": [b_row["Average First Kills"]],
            "Team B Average First Deaths Per Round": [b_row["Average First Deaths Per Round"]],
        }

        df = pd.DataFrame(pred_df)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = add_engineered_features(df.fillna(0))
        return df[self.feature_cols].fillna(0)

    def _win_probability_team1(self, team1: str, team2: str) -> float:
        df_12 = self.build_pred_df(team1, team2)
        df_21 = self.build_pred_df(team2, team1)
        p1 = float(self.rf_model.predict_proba(df_12)[0][1])
        p2 = float(self.rf_model.predict_proba(df_21)[0][1])
        return (p1 + (1.0 - p2)) / 2.0

    def predict_match(self, team1: str, team2: str, threshold: float = 0.5) -> dict:
        p1 = self._win_probability_team1(team1, team2)
        p1_pct = round(p1 * 100, 1)
        favored = team1 if p1 >= 0.5 else team2

        feature_df = self.build_pred_df(team1, team2)
        map_preds = sort_map_predictions(
            self.map_predictor.predict_maps(team1, team2, p1_pct)
        )

        return {
            "team1_win_probability": p1_pct,
            "team2_win_probability": round((1.0 - p1) * 100, 1),
            "team1_win_prediction": p1 >= threshold,
            "confidence": confidence_label(p1_pct),
            "key_factors": build_key_factors(
                team1,
                team2,
                favored,
                feature_df.iloc[0],
                self.recent_form,
                self.agent_diversity,
            ),
            "map_predictions": map_preds,
            "series_predictions": {
                "bo3": simulate_series(map_preds, best_of=3),
                "bo5": simulate_series(map_preds, best_of=5),
            },
            "recent_form": {
                team1: round(self.recent_form.get(team1, 50.0), 1),
                team2: round(self.recent_form.get(team2, 50.0), 1),
            },
        }

    def prediction_probability(self, teama, teamb, threshold=0.5):
        return 1 if self.predict_match(teama, teamb, threshold)["team1_win_prediction"] else 0
