import TeamCard from '../components/TeamCard'
import '../css/Matchup.css'

function Matchup({ team1, team2 }) {
  return (
    <div className="matchup">
      <div className="team-slot">
        {team1 ? <TeamCard team={team1} /> : <p>Select Team 1</p>}
      </div>

      <div className="vs">VS</div>

      <div className="team-slot">
        {team2 ? <TeamCard team={team2} /> : <p>Select Team 2</p>}
      </div>
    </div>
  )
}

export default Matchup
