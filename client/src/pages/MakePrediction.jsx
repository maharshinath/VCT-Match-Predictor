import '../css/Home.css'
import { useState, useEffect} from "react"
import { useNavigate } from 'react-router-dom'
import { getTeams } from '../services/api'
import Matchup from '../components/Matchup'
import '../css/Dropdowns.css'

function MakePrediction() {
    const [teams, setTeams] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Use empty string instead of null so <select> resets correctly
    const [team1, setTeam1] = useState("")
    const [team2, setTeam2] = useState("")
    const navigate = useNavigate()

    useEffect(() => {
        const loadTeams = async () => {
            try {
                const allteams = await getTeams()
                if (!Array.isArray(allteams) || allteams.length === 0) {
                    throw new Error('No teams returned from API')
                }
                setTeams(allteams)
                setError(null)
            } catch (err) {
                console.error(err)
                setError('Could not load teams. Make sure the backend is running at http://127.0.0.1:5001')
            } finally {
                setLoading(false)
            }
        }
        loadTeams()
    }, [])

    const clearMatch = () => {
        setTeam1("")
        setTeam2("")
    }

    const handlePredict = () => {
        // Navigate to prediction page
        navigate('/predict/' + teams[team1].Team + '/' + teams[team2].Team)
    }

    const handleTeam1Change = (e) => {
        const selectedIndex = e.target.value
        // If the selected team is the same as team2, clear team2
        if (selectedIndex === team2) {
            setTeam2("")
        }
        setTeam1(selectedIndex)
    }

    const handleTeam2Change = (e) => {
        const selectedIndex = e.target.value
        // If the selected team is the same as team1, clear team1
        if (selectedIndex === team1) {
            setTeam1("")
        }
        setTeam2(selectedIndex)
    }

    return (
        <div className="home make-prediction">
            <div className="text-content">
                <h1>VCT Match Predictor</h1>
                <p>Predict the outcome of VCT matches using machine learning</p>
            </div>

            {/* Send actual team objects to Matchup */}
            <Matchup 
                team1={team1 !== "" ? teams[team1] : null} 
                team2={team2 !== "" ? teams[team2] : null} 
            />

            {error && <p className="error-message">{error}</p>}

            {loading ? (
                <p>Loading teams...</p>
            ) : (
                <div className="dropdowns">
                    {/* TEAM 1 */}
                    <select 
                        id="team1" 
                        value={team1} 
                        onChange={handleTeam1Change}
                    >
                        <option value="">Select Team 1</option>
                        {teams.map((team, index) => {
                            // Exclude team2 from team1 dropdown
                            if (index.toString() === team2) return null
                            return (
                                <option key={team.id} value={index}>
                                    {team.Team}
                                </option>
                            )
                        })}
                    </select>

                    {/* TEAM 2 */}
                    <select 
                        id="team2" 
                        value={team2} 
                        onChange={handleTeam2Change}
                    >
                        <option value="">Select Team 2</option>
                        {teams.map((team, index) => {
                            // Exclude team1 from team2 dropdown
                            if (index.toString() === team1) return null
                            return (
                                <option key={team.id} value={index}>
                                    {team.Team}
                                </option>
                            )
                        })}
                    </select>
                </div>
            )}

            {/* BUTTONS */}
            <div className="buttons">
                <button onClick={clearMatch}>Clear Match</button>

                <button 
                    disabled={team1 === "" || team2 === ""}
                    onClick={handlePredict}
                >
                    Predict
                </button>
            </div>
        </div>
    )
}

export default MakePrediction
