import { useEffect, useState } from 'react'
import MapPredictions from './MapPredictions'
import TeamRoster from './TeamRoster'
import TeamStatsDashboard from './TeamDashboard'
import '../css/Prediction.css'

const API_ORIGIN = 'http://127.0.0.1:5001'
const DEFAULT_LOGO = `${API_ORIGIN}/static/logos/default-logo.svg`

const TABS = [
  { id: 'maps', label: 'Map Predictions' },
  { id: 'stats', label: 'Stats' },
  { id: 'winner', label: 'Breakdown' },
  { id: 'roster', label: 'Roaster' },
]

function logoUrl(path) {
  if (!path) return DEFAULT_LOGO
  return path.startsWith('/') ? `${API_ORIGIN}${path}` : `${API_ORIGIN}/${path}`
}

function Prediction({
  team1,
  team2,
  result,
  matchupData,
  team1Roster,
  team2Roster,
  rosterLoading,
  rosterError,
  onRosterTabOpen,
}) {
  const [revealed, setRevealed] = useState(false)
  const [activeTab, setActiveTab] = useState('winner')

  useEffect(() => {
    setRevealed(false)
    let frame2 = 0
    const frame1 = requestAnimationFrame(() => {
      frame2 = requestAnimationFrame(() => setRevealed(true))
    })
    const fallback = window.setTimeout(() => setRevealed(true), 120)
    return () => {
      cancelAnimationFrame(frame1)
      cancelAnimationFrame(frame2)
      window.clearTimeout(fallback)
    }
  }, [result, team1?.Team, team2?.Team])

  useEffect(() => {
    setActiveTab('winner')
  }, [result, team1?.Team, team2?.Team])

  const selectTab = (tabId) => {
    setActiveTab(tabId)
    if (tabId === 'roster') onRosterTabOpen?.()
  }

  if (!team1 || !team2 || !result) return null

  const team1Wins = result.team1_win_prediction
  const winner = team1Wins ? team1 : team2
  const confidence = result.confidence
  const winnerProb = team1Wins ? result.team1_win_probability : result.team2_win_probability

  return (
    <div className={`prediction-container ${revealed ? 'is-revealed' : ''}`}>
      {revealed && <div className="winner-celebration-burst" aria-hidden="true" />}
      <div className="prediction-header">
        <h3>Match winner prediction</h3>
        {confidence && (
          <span className={`confidence-badge confidence-${confidence.level}`}>
            {confidence.label}
          </span>
        )}
      </div>

      <div className={`prediction-teams-strip${revealed ? ' is-revealed' : ''}`}>
        <div className="matchup-stage">
          <article
            className={`matchup-slot${team1Wins ? ' matchup-slot--winner' : ' matchup-slot--loser'}`}
          >
            {team1Wins && (
              <>
                <div className="matchup-winner-glow" aria-hidden="true" />
                <div className="matchup-winner-shimmer" aria-hidden="true" />
                <span className="matchup-pick-label">Predicted</span>
              </>
            )}
            <div className="matchup-slot-content">
              <div className="matchup-logo-wrap">
                <img
                  src={logoUrl(team1['Image Path'])}
                  alt={team1.Team}
                  className="matchup-logo"
                  onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
                />
              </div>
              <div className="matchup-meta">
                <span className="matchup-name">{team1.Team}</span>
                {team1.Region && <span className="matchup-region">{team1.Region}</span>}
              </div>
            </div>
          </article>

          <div className="matchup-center">
            <span className="matchup-vs">VS</span>
            <span
              className={`matchup-pointer${team1Wins ? ' matchup-pointer--left' : ' matchup-pointer--right'}`}
              aria-hidden="true"
            />
          </div>

          <article
            className={`matchup-slot${!team1Wins ? ' matchup-slot--winner' : ' matchup-slot--loser'}`}
          >
            {!team1Wins && (
              <>
                <div className="matchup-winner-glow" aria-hidden="true" />
                <div className="matchup-winner-shimmer" aria-hidden="true" />
                <span className="matchup-pick-label">Predicted</span>
              </>
            )}
            <div className="matchup-slot-content">
              <div className="matchup-logo-wrap">
                <img
                  src={logoUrl(team2['Image Path'])}
                  alt={team2.Team}
                  className="matchup-logo"
                  onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
                />
              </div>
              <div className="matchup-meta">
                <span className="matchup-name">{team2.Team}</span>
                {team2.Region && <span className="matchup-region">{team2.Region}</span>}
              </div>
            </div>
          </article>
        </div>
      </div>

      <div className="prediction-tabs-footer">
        <div className="prediction-tabs" role="tablist" aria-label="Prediction details">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
              className={`prediction-tab${activeTab === tab.id ? ' is-active' : ''}`}
              onClick={() => selectTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab && (
          <div
            className="prediction-tab-panel"
            role="tabpanel"
            id={`panel-${activeTab}`}
            aria-labelledby={`tab-${activeTab}`}
          >
            {activeTab === 'winner' && (
              <div className="prediction-content prediction-tab-winner">
                <div className="prediction-result glass">
                  <div className="winner-announcement">
                    <span className="predicted-text">Predicted winner</span>
                    <img
                      className="winner-announcement-logo"
                      src={logoUrl(winner['Image Path'])}
                      alt=""
                      onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
                    />
                    <span className="winner-name">{winner.Team}</span>
                    {winnerProb != null && (
                      <span className="winner-chance-badge">{winnerProb}% win chance</span>
                    )}
                    {result.team1_win_probability != null && (
                      <span className="match-win-chance">
                        {team1.Team} {result.team1_win_probability}% · {team2.Team}{' '}
                        {result.team2_win_probability}%
                      </span>
                    )}
                  </div>

                  {result.key_factors?.length > 0 && (
                    <div className="key-factors">
                      <h4>Why {winner.Team} is favored</h4>
                      <ul>
                        {result.key_factors.map((f) => (
                          <li key={f.label}>
                            <strong>{f.label}:</strong> {f.detail}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <p className="prediction-disclaimer">
                    Estimates from historical VCT data. Not betting odds; does not account for
                    live roster changes or map veto order.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'roster' && (
              <>
                {rosterLoading && <p className="tab-panel-message">Loading rosters…</p>}
                {rosterError && <p className="tab-panel-error">{rosterError}</p>}
                {!rosterLoading && !rosterError && (
                  <div className="rosters-panel">
                    <TeamRoster teamName={team1.Team} roster={team1Roster} playersOnly />
                    <TeamRoster teamName={team2.Team} roster={team2Roster} playersOnly />
                  </div>
                )}
              </>
            )}

            {activeTab === 'maps' && (
              <MapPredictions
                team1={team1}
                team2={team2}
                mapPredictions={result.map_predictions}
                embedded
              />
            )}

            {activeTab === 'stats' && matchupData && (
              <TeamStatsDashboard
                team1={team1}
                team2={team2}
                matchupData={matchupData}
                embedded
              />
            )}

            {activeTab === 'stats' && !matchupData && (
              <p className="tab-panel-message">Stats unavailable for this matchup.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Prediction
