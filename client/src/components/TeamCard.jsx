import { logoUrl, DEFAULT_LOGO } from '../config'
import '../css/TeamCard.css'

function TeamCard({team}) {
    
    return (
        <div className="card">
            <img
                src={logoUrl(team["Image Path"])}
                alt={team["Team"]}
                onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
            />
            <h2>{team["Team"]}</h2>
            {team["Region"] && <p className="team-region">{team["Region"]}</p>}
        </div>
    )
}

export default TeamCard