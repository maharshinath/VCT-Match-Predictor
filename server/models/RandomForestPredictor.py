import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))




class RandomForestPredictor:
    def __init__(self):
        self.rf_model = joblib.load(os.path.join(BASE_DIR, 'rf.pkl'))
        self.team_data = pd.read_csv(os.path.join(BASE_DIR, '../csv/team_data.csv'))
        self.match_data = pd.read_csv(os.path.join(BASE_DIR, '../csv/scores.csv'))
        self.feature_cols = [
        'Team A Winrate vs B', 'Team A Winrate', 'Team A K/D Ratio', 'Team A Average Damage',
        'Team A Average Combat Score', 'Team A Average First Kills', 'Team A Average First Deaths Per Round',
        'Team B Winrate vs A', 'Team B Winrate', 'Team B K/D Ratio', 'Team B Average Damage',
        'Team B Average Combat Score', 'Team B Average First Kills', 'Team B Average First Deaths Per Round'
        ]

    def get_past_matches(self, team1, team2):
        match_data = self.match_data
        match_data = match_data.dropna()
        filtered_df = match_data[(match_data['Match Name'] == team1 + " vs " + team2) | (match_data['Match Name'] == team2 + " vs " + team1)]

        matches = set()
        for i in range(len(filtered_df) - 1, -1, -1):
            matches.add((filtered_df.iloc[i]['Match Result']))

        return matches

    def get_winrate_team1(self, team1, team2):
        match_set = self.get_past_matches(team1, team2)
        if len(match_set) == 0:
            return None
        wins = 0
        for match in match_set:
            if match ==(team1 + " won"):
                wins += 1
        return wins/len(match_set) * 100

    def build_pred_df(self, teama, teamb):
        # Get team data with proper error handling
        a_data = self.team_data.loc[self.team_data['Team'] == teama]
        b_data = self.team_data.loc[self.team_data['Team'] == teamb]
        
        # Check if teams exist
        if a_data.empty:
            raise ValueError(f"Team '{teama}' not found in team data")
        if b_data.empty:
            raise ValueError(f"Team '{teamb}' not found in team data")
        
        # Get first row and convert to scalar values
        a_row = a_data.iloc[0]
        b_row = b_data.iloc[0]

        winrate_team1 = self.get_winrate_team1(teama, teamb)
        if winrate_team1 is None:
            winrate_team1 = 0
            winrate_team2 = 0
        else:
            winrate_team2 = 100 - winrate_team1
        
        # Build prediction dictionary with scalar values
        pred_df = {
            'Team A Winrate vs B': [winrate_team1],
            'Team A Winrate': [a_row["Winrate"]],
            'Team A K/D Ratio': [a_row["K/D Ratio"]],
            'Team A Average Damage': [a_row["Average Damage"]],
            'Team A Average Combat Score': [a_row["Average Combat Score"]],
            'Team A Average First Kills': [a_row["Average First Kills"]],
            'Team A Average First Deaths Per Round': [a_row["Average First Deaths Per Round"]],
            'Team B Winrate vs A': [winrate_team2],
            'Team B Winrate': [b_row["Winrate"]],
            'Team B K/D Ratio': [b_row["K/D Ratio"]],
            'Team B Average Damage': [b_row["Average Damage"]],
            'Team B Average Combat Score': [b_row["Average Combat Score"]],
            'Team B Average First Kills': [b_row["Average First Kills"]],
            'Team B Average First Deaths Per Round': [b_row["Average First Deaths Per Round"]]
        }
        
        df = pd.DataFrame(pred_df)
        
        # Additional safety check - ensure all values are numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any NaN values with 0 (or appropriate defaults)
        df = df.fillna(0)
        
        return df
    


    def prediction_probability(self, teama, teamb, threshold=0.5):
        # Test both team orders
        df_ab = self.build_pred_df(teama, teamb)
        
        prob_a_wins_ab = self.rf_model.predict_proba(df_ab)[0][1]
        return 1 if prob_a_wins_ab>= threshold else 0