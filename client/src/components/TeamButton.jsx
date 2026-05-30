

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
                <img className="button_icon" src={`http://127.0.0.1:5001/${team["Image Path"]}`} alt={team["Team"]} />
                {team["Team"]}
            </button>
        </div>
    )
}

export default TeamButton