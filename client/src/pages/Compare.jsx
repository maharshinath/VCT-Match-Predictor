import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getTeams } from '../services/api'
import '../css/Compare.css'

function Compare() {
  const [teams, setTeams] = useState([])
  const [team1, setTeam1] = useState('')
  const [team2, setTeam2] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    getTeams().then(setTeams).catch(console.error)
  }, [])

  const handleCompare = () => {
    const t1 = teams[team1]?.Team
    const t2 = teams[team2]?.Team
    if (t1 && t2 && t1 !== t2) {
      navigate(`/predict/${encodeURIComponent(t1)}/${encodeURIComponent(t2)}`)
    }
  }

  return (
    <div className="compare-page">
      <h1>Compare teams</h1>
      <p>Pick any two VCT teams to view stats, rosters, and predictions.</p>
      <div className="compare-dropdowns">
        <select value={team1} onChange={(e) => setTeam1(e.target.value)}>
          <option value="">Team 1</option>
          {teams.map((t, i) => (
            <option key={t.id} value={i} disabled={i.toString() === team2}>
              {t.Team}
            </option>
          ))}
        </select>
        <select value={team2} onChange={(e) => setTeam2(e.target.value)}>
          <option value="">Team 2</option>
          {teams.map((t, i) => (
            <option key={t.id} value={i} disabled={i.toString() === team1}>
              {t.Team}
            </option>
          ))}
        </select>
      </div>
      <button
        type="button"
        disabled={team1 === '' || team2 === '' || team1 === team2}
        onClick={handleCompare}
      >
        View matchup
      </button>
    </div>
  )
}

export default Compare
