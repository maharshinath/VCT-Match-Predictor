

import '../css/TeamButton.css'

const API_ORIGIN = "http://127.0.0.1:5001"
const DEFAULT_LOGO = `${API_ORIGIN}/static/logos/default-logo.svg`

function logoUrl(path) {
    if (!path) return DEFAULT_LOGO
    return path.startsWith("/") ? `${API_ORIGIN}${path}` : `${API_ORIGIN}/${path}`
}

function TeamButton({ team, onTeamSelect, isSelected }) {
    const handleClick = () => {
        onTeamSelect(team);
    };

    return (
        <div className="team-button">
            <button 
                className={`pick glass ${isSelected ? 'selected' : ''}`}
                onClick={handleClick}
            >
                <img
                    className="button_icon"
                    src={logoUrl(team["Image Path"])}
                    alt={team["Team"]}
                    onError={(e) => { e.currentTarget.src = DEFAULT_LOGO }}
                />
                {team["Team"]}
            </button>
        </div>
    )
}

export default TeamButton