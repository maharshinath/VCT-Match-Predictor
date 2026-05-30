import TeamCard from '../components/TeamCard'
import '../css/Matchup.css'

function Matchup({ team1, team2 }) {
  if (!team1 || !team2) return null

  return (
    <div className="matchup">
      <div className="team-slot">
        <TeamCard team={team1} />
      </div>

      <div className="vs">VS</div>

      <div className="team-slot">
        <TeamCard team={team2} />
      </div>
    </div>
  )
}

export default Matchup
