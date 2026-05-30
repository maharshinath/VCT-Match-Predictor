from flask import Flask, request
from flask_restful import Resource, Api
from models.RandomForestPredictor import RandomForestPredictor as Predictor
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)
api = Api(app)

predictor = Predictor()

class TeamData(Resource):
    def get(self, team):
        if not team:
            return {'error': 'Query Parameter Required'}
        

        rows = predictor.team_data[predictor.team_data['Team'] == team]
        return rows.to_dict(orient="records")
    
class TeamsData(Resource):
    def get(self):
        return predictor.team_data.to_dict(orient="records")


class PredictorMatchup(Resource):
    def get(self, team1, team2):

        if not team1 or not team2:
            return {'error': 'Both team1 and team2 query parameters are required'}, 400

        try:
            prediction = predictor.prediction_probability(team1, team2)
            return {
                'team1': team1,
                'team2': team2,
                'team1_win_prediction': bool(prediction)
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}, 500

class MatchupData(Resource):
    def get(self, team1, team2):

        if not team1 or not team2:
            return {'error': 'Both team1 and team2 query parameters are required'}, 400

        data = predictor.build_pred_df(team1, team2)

        return data.to_json(orient="records")

api.add_resource(TeamData, '/api/info/<team>')
api.add_resource(TeamsData, '/api/teams')
api.add_resource(PredictorMatchup, '/api/predict/<team1>/<team2>')
api.add_resource(MatchupData, '/api/matchup_data/<team1>/<team2>')


@app.route('/')
def home():
    return '<div></div>'


if __name__ == '__main__':
    app.run(debug=True)
