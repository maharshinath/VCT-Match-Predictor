import json
from pathlib import Path

from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS

from models.RandomForestPredictor import RandomForestPredictor as Predictor
from roster import get_team_roster
from vct_config import COMP_POOL_MAPS

app = Flask(__name__, static_url_path="/static", static_folder="static")
CORS(app)
api = Api(app)

predictor = Predictor()
SERVER_DIR = Path(__file__).resolve().parent
METRICS_PATH = SERVER_DIR / "data" / "model_metrics.json"


def load_model_metrics() -> dict:
    if METRICS_PATH.exists():
        try:
            return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "random_split_accuracy": 72.8,
        "time_ordered_split_accuracy": None,
        "note": "Run python scripts/evaluate_model.py to refresh metrics.",
    }


class TeamData(Resource):
    def get(self, team):
        if not team:
            return {"error": "Query Parameter Required"}
        rows = predictor.team_data[predictor.team_data["Team"] == team]
        return rows.to_dict(orient="records")


class TeamsData(Resource):
    def get(self):
        return predictor.team_data.to_dict(orient="records")


class PredictorMatchup(Resource):
    def get(self, team1, team2):
        if not team1 or not team2:
            return {"error": "Both team1 and team2 query parameters are required"}, 400
        try:
            result = predictor.predict_match(team1, team2)
            return {"team1": team1, "team2": team2, **result}, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}, 500


class MatchupData(Resource):
    def get(self, team1, team2):
        if not team1 or not team2:
            return {"error": "Both team1 and team2 query parameters are required"}, 400
        data = predictor.build_pred_df(team1, team2)
        return data.to_dict(orient="records")


class TeamRoster(Resource):
    def get(self, team):
        if not team:
            return {"error": "Team name is required"}, 400
        rows = predictor.team_data[predictor.team_data["Team"] == team]
        if rows.empty:
            return {"error": f"Team '{team}' not found"}, 404
        return get_team_roster(team), 200


class MetaData(Resource):
    def get(self):
        return {
            "comp_pool_maps": COMP_POOL_MAPS,
            "standard_maps": 12,
            "model_metrics": load_model_metrics(),
        }, 200


api.add_resource(TeamData, "/api/info/<team>")
api.add_resource(TeamsData, "/api/teams")
api.add_resource(PredictorMatchup, "/api/predict/<team1>/<team2>")
api.add_resource(MatchupData, "/api/matchup_data/<team1>/<team2>")
api.add_resource(TeamRoster, "/api/roster/<team>")
api.add_resource(MetaData, "/api/meta")


@app.route("/")
def home():
    return "<div></div>"


if __name__ == "__main__":
    app.run(debug=True)
