import { getMapSplashUrl } from '../data/mapImages'
import '../css/MapPredictions.css'

const API_ORIGIN = 'http://127.0.0.1:5001'
const DEFAULT_LOGO = `${API_ORIGIN}/static/logos/default-logo.svg`

function logoUrl(path) {
  if (!path) return DEFAULT_LOGO
  return path.startsWith('/') ? `${API_ORIGIN}${path}` : `${API_ORIGIN}/${path}`
}

function MapPredictions({ team1, team2, mapPredictions, embedded = false }) {
  if (!mapPredictions?.length || !team1 || !team2) return null

  const sortedMaps = [...mapPredictions].sort((a, b) =>
    a.map.localeCompare(b.map, undefined, { sensitivity: 'base' })
  )

  return (
    <section className={`map-predictions${embedded ? ' map-predictions--embedded' : ''}`}>
      <h4>Map Predictions</h4>
      <p className="map-predictions-intro">
        If each map is played — who is more likely to win? Maps listed A–Z.
      </p>
      <ul className="map-prediction-list">
        {sortedMaps.map((entry) => {
          const team1Favored = entry.favored_team === team1.Team
          const favoredTeam = team1Favored ? team1 : team2
          const favoredName = favoredTeam.Team
          const favoredPct = team1Favored
            ? entry.team1_win_probability
            : entry.team2_win_probability
          const splashUrl = getMapSplashUrl(entry.map)

          return (
            <li
              key={entry.map}
              className={`map-prediction-item${splashUrl ? ' has-map-art' : ''}`}
            >
              {splashUrl && (
                <img
                  className="map-prediction-art"
                  src={splashUrl}
                  alt=""
                  loading="lazy"
                  aria-hidden="true"
                />
              )}
              <div className="map-prediction-content">
                <div className="map-prediction-header">
                  <span className="map-pick-label">{entry.map}</span>
                  <span className="map-pick-winner">
                    <img
                      className="map-pick-winner-logo"
                      src={logoUrl(favoredTeam['Image Path'])}
                      alt=""
                      loading="lazy"
                      onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
                    />
                    <span className="map-pick-winner-text">
                      {favoredName} <strong>{favoredPct}%</strong>
                    </span>
                  </span>
                </div>
                <div className="map-prob-track">
                  <div
                    className="map-prob-fill-team1"
                    style={{ width: `${entry.team1_win_probability}%` }}
                  />
                </div>
                <div className="map-prob-teams">
                  <span className={team1Favored ? 'favored' : ''}>
                    {team1.Team} {entry.team1_win_probability}%
                  </span>
                  <span className={!team1Favored ? 'favored' : ''}>
                    {team2.Team} {entry.team2_win_probability}%
                  </span>
                </div>
              </div>
            </li>
          )
        })}
      </ul>
    </section>
  )
}

export default MapPredictions
