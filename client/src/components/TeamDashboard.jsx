import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import '../css/TeamDashboard.css'

const API_ORIGIN = 'http://127.0.0.1:5001'
const DEFAULT_LOGO = `${API_ORIGIN}/static/logos/default-logo.svg`

function logoUrl(path) {
  if (!path) return DEFAULT_LOGO
  return path.startsWith('/') ? `${API_ORIGIN}${path}` : `${API_ORIGIN}/${path}`
}

function betterTeamForStat(a, b, team1, team2) {
  if (a == null || b == null || Number.isNaN(Number(a)) || Number.isNaN(Number(b))) return null
  if (a === b) return null
  return b > a ? team2 : team1
}

const CHART_TOOLTIP_STYLE = {
  backgroundColor: '#1a2332',
  border: '1px solid rgba(255,255,255,0.12)',
  borderRadius: '8px',
  color: '#f4f7fb',
  fontSize: '13px',
}

function fmt(value, digits = 1) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return Number(value).toFixed(digits)
}

function diffClass(a, b) {
  const d = b - a
  if (d > 0) return 'diff-positive'
  if (d < 0) return 'diff-negative'
  return ''
}

const TeamStatsDashboard = ({ team1, team2, matchupData, embedded = false }) => {
  const rawData = {
    h2hA: matchupData['Team A Winrate vs B'],
    h2hB: matchupData['Team B Winrate vs A'],
    winA: team1.Winrate,
    winB: team2.Winrate,
    kdA: team1['K/D Ratio'],
    kdB: team2['K/D Ratio'],
    dmgA: team1['Average Damage'],
    dmgB: team2['Average Damage'],
    acsA: team1['Average Combat Score'],
    acsB: team2['Average Combat Score'],
    fkA: team1['Average First Kills'],
    fkB: team2['Average First Kills'],
  }

  const t1Name = team1.Team
  const t2Name = team2.Team

  const barData = [
    { stat: 'Winrate %', [t1Name]: rawData.winA, [t2Name]: rawData.winB },
    { stat: 'K/D', [t1Name]: rawData.kdA, [t2Name]: rawData.kdB },
    { stat: 'Damage', [t1Name]: rawData.dmgA, [t2Name]: rawData.dmgB },
    { stat: 'ACS', [t1Name]: rawData.acsA, [t2Name]: rawData.acsB },
    { stat: 'First kills', [t1Name]: rawData.fkA, [t2Name]: rawData.fkB },
  ]

  const tableRows = [
    { label: 'Overall winrate', a: rawData.winA, b: rawData.winB, suffix: '%', digits: 1 },
    { label: 'K/D ratio', a: rawData.kdA, b: rawData.kdB, digits: 3 },
    { label: 'Avg damage', a: rawData.dmgA, b: rawData.dmgB, digits: 1 },
    { label: 'Avg combat score', a: rawData.acsA, b: rawData.acsB, digits: 1 },
    { label: 'Avg first kills', a: rawData.fkA, b: rawData.fkB, digits: 2 },
  ]

  return (
    <div className={`stats-dashboard${embedded ? ' stats-dashboard--embedded' : ''}`}>
      {!embedded && (
        <header className="stats-dashboard__header">
          <h2 className="stats-dashboard__title">Team comparison</h2>
          <p className="stats-dashboard__subtitle">
            Historical VCT stats for {t1Name} vs {t2Name}
          </p>
        </header>
      )}

      <div className="stats-h2h">
        <div className="stats-h2h-card team-a">
          <span className="label">{t1Name} H2H winrate</span>
          <span className="value">{fmt(rawData.h2hA, 0)}%</span>
        </div>
        <div className="stats-h2h-card team-b">
          <span className="label">{t2Name} H2H winrate</span>
          <span className="value">{fmt(rawData.h2hB, 0)}%</span>
        </div>
      </div>

      <div className="stats-chart-card">
        <h3>Performance overview</h3>
        <div className="stats-chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 8, right: 12, left: 0, bottom: 48 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="stat"
                tick={{ fill: 'rgba(244,247,251,0.55)', fontSize: 11 }}
                angle={-28}
                textAnchor="end"
                height={56}
              />
              <YAxis tick={{ fill: 'rgba(244,247,251,0.55)', fontSize: 11 }} />
              <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
              <Bar dataKey={t1Name} fill="var(--color-team-a)" radius={[4, 4, 0, 0]} />
              <Bar dataKey={t2Name} fill="var(--color-team-b)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="stats-table-card">
        <h3>Detailed metrics</h3>
        <div className="stats-table-scroll">
          <table className="stats-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th className="col-team-a">{t1Name}</th>
                <th className="col-team-b">{t2Name}</th>
                <th>Δ</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row) => {
                const leader = betterTeamForStat(row.a, row.b, team1, team2)
                return (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td className="col-team-a">
                    {fmt(row.a, row.digits)}{row.suffix || ''}
                  </td>
                  <td className="col-team-b">
                    {fmt(row.b, row.digits)}{row.suffix || ''}
                  </td>
                  <td className={`stats-diff-cell ${diffClass(row.a, row.b)}`}>
                    <span className="stats-diff-value">
                      {fmt(row.b - row.a, row.digits)}{row.suffix || ''}
                    </span>
                    {leader && (
                      <img
                        className="stats-diff-logo"
                        src={logoUrl(leader['Image Path'])}
                        alt=""
                        title={leader.Team}
                        onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
                      />
                    )}
                  </td>
                </tr>
              )})}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default TeamStatsDashboard
