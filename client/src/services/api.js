const BASE_URL = "http://127.0.0.1:5001/api"


export const getPrediction = async(team1, team2) => {
    console.log(`${BASE_URL}/predict/${team1}/${team2}`)
    const result = await fetch(`${BASE_URL}/predict/${encodeURIComponent(team1)}/${encodeURIComponent(team2)}`)
    if (!result.ok) throw new Error('Prediction failed');
    return await result.json()
}


export const getMatchupData = async(team1, team2) => {
    const result = await fetch(`${BASE_URL}/matchup_data/${encodeURIComponent(team1)}/${encodeURIComponent(team2)}`)
    if (!result.ok) throw new Error('Prediction failed');
    return await result.json()
}


const parseTeamsPayload = (data) => {
    if (Array.isArray(data)) return data
    if (typeof data === 'string') return JSON.parse(data)
    throw new Error('Unexpected teams response format')
}

export const getTeams = async() => {
    const response = await fetch(`${BASE_URL}/teams`)
    if (!response.ok) throw new Error(`Failed to load teams (${response.status})`)
    const data = await response.json()
    return parseTeamsPayload(data)
}


export const getTeamData = async(team) => {
    const response = await fetch(`${BASE_URL}/info/${encodeURIComponent(team)}`)
    if (!response.ok) throw new Error(`Failed to load team (${response.status})`)
    const data = await response.json()
    return parseTeamsPayload(data)
}