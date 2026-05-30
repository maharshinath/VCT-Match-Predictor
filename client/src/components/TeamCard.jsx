import '../css/TeamCard.css'


function TeamCard({team}) {
    
    return (
        <div className="card">
            <img src={`http://127.0.0.1:5001/${team["Image Path"]}`}></img>
            <h2>{team["Team"]}</h2>
        </div>
    )
}

export default TeamCard