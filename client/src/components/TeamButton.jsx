
import { logoUrl, DEFAULT_LOGO } from '../config'
import '../css/TeamButton.css'

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