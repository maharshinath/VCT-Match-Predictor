import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

vct_data = pd.read_csv('model/data/filtered_matches.csv')

feature_cols = [
    'Team A Winrate vs B', 'Team A Winrate', 'Team A K/D Ratio', 'Team A Average Damage',
    'Team A Average Combat Score', 'Team A Average First Kills', 'Team A Average First Deaths Per Round',
    'Team B Winrate vs A', 'Team B Winrate', 'Team B K/D Ratio', 'Team B Average Damage',
    'Team B Average Combat Score', 'Team B Average First Kills', 'Team B Average First Deaths Per Round'
]

#fix order sensitivity by creating order-invariant dataset
def create_order_invariant_data(df):
    #swapping team positions 
    original_data = df.copy()
    
    # Create swapped version
    swapped_data = df.copy()
    
    # Swap Team A and Team B columns
    team_a_cols = [col for col in feature_cols if 'Team A' in col]
    team_b_cols = [col for col in feature_cols if 'Team B' in col]
    
    for a_col, b_col in zip(team_a_cols, team_b_cols):
        swapped_data[a_col] = df[b_col]
        swapped_data[b_col] = df[a_col]
    
    # Flip the target variable for swapped data
    swapped_data['Team A Win'] = 1 - df['Team A Win']
    
    # Combine original and swapped data
    augmented_data = pd.concat([original_data, swapped_data], ignore_index=True)
    return augmented_data




def prediction(df):
    rf_augmented = joblib.load('model/rf_augmented_model.pkl')
    pred = rf_augmented.predict(df)
    return pred[0]  

def prediction_probability(df, threshold=0.5):
    rf_augmented = joblib.load('model/rf_augmented_model.pkl')
    prob = rf_augmented.predict_proba(df)
    team_a_win_prob = prob[0][1]  # Probability of Team A winning
    return 1 if team_a_win_prob >= threshold else 0


# augmented_vct_data = create_order_invariant_data(vct_data)

# x_augmented = augmented_vct_data[feature_cols]
# y_augmented = augmented_vct_data['Team A Win'].astype(int)

# X_train, X_test, y_train, y_test = train_test_split(x_augmented, y_augmented, test_size=0.2, random_state=42)

# rf_augmented = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
# rf_augmented.fit(X_train, y_train)

# joblib.dump(rf_augmented, 'rf_augmented_model.pkl')
# joblib.dump(X_test, 'x_test.pkl')
# joblib.dump(y_test, 'y_test.pkl')


# X_test = joblib.load('x_test.pkl')
# y_test = joblib.load('y_test.pkl')
# print("Accuracy:", rf_augmented.score(X_test, y_test))