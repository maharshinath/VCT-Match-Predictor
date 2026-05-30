import '../css/TeamCard.css'


const API_ORIGIN = "http://127.0.0.1:5001"
const DEFAULT_LOGO = `${API_ORIGIN}/static/logos/default-logo.svg`

function logoUrl(path) {
    if (!path) return DEFAULT_LOGO
    return path.startsWith("/") ? `${API_ORIGIN}${path}` : `${API_ORIGIN}/${path}`
}

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