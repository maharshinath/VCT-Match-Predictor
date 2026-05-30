import '../css/Prediction.css'

function Prediction({ team1, team2, result }) {
  if (!team1 || !team2 || !result) return null

  const winner = result.team1_win_prediction ? team1 : team2

  return (
    <div className="prediction-container">
      <div className="prediction-header">
        <h3>Match Prediction</h3>
      </div>

      <div className="prediction-content">
        <div className="teams-comparison glass">
          <div className={`team-result ${result.team1_win_prediction ? 'winner' : 'loser'}`}>
            <img
              src={`http://127.0.0.1:5001${team1["Image Path"]}`}
              alt={team1["Team"]}
              className="team-logo"
            />
            <span className="team-name">{team1["Team"]}</span>
            {result.team1_win_prediction && <div className="winner-crown">👑</div>}
          </div>

          <div className="vs-section">
            <span className="vs-text">VS</span>
            <div className="prediction-arrow">
              {result.team1_win_prediction ? '←' : '→'}
            </div>
          </div>

          <div className={`team-result ${!result.team1_win_prediction ? 'winner' : 'loser'}`}>
            <img
              src={`http://127.0.0.1:5001/${team2["Image Path"]}`}
              alt={team2["Team"]}
              className="team-logo"
            />
            <span className="team-name">{team2["Team"]}</span>
            {!result.team1_win_prediction && <div className="winner-crown">👑</div>}
          </div>
        </div>

        <div className="prediction-result glass">
          <div className="winner-announcement">
            <span className="predicted-text">Predicted Winner:</span>
            <span className="winner-name">{winner["Team"]}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Prediction
