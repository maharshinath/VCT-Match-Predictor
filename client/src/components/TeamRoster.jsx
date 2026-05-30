import '../css/TeamRoster.css'

function PersonList({ title, people, emptyLabel }) {
  if (!people?.length) {
    return (
      <div className="roster-section">
        <h4>{title}</h4>
        <p className="roster-empty">{emptyLabel}</p>
      </div>
    )
  }

  return (
    <div className="roster-section">
      <h4>{title}</h4>
      <ul className="roster-list">
        {people.map((person) => (
          <li key={`${person.ign}-${person.role || title}`}>
            <span className="roster-ign">{person.ign}</span>
            {person.name && <span className="roster-name">{person.name}</span>}
            {person.role && <span className="roster-role">{person.role}</span>}
          </li>
        ))}
      </ul>
    </div>
  )
}

function TeamRoster({ teamName, roster, playersOnly = false }) {
  if (!roster) return null

  return (
    <div className="team-roster glass">
      <h3 className="roster-team-title">{teamName}</h3>
      <PersonList
        title="Players"
        people={roster.players}
        emptyLabel="Roster unavailable"
      />
      {!playersOnly && roster.coaches?.length > 0 && (
        <PersonList
          title="Coaching staff"
          people={roster.coaches}
          emptyLabel="Coach info unavailable"
        />
      )}
      {roster.source === 'dataset' && (
        <p className="roster-note">Players from match data; live roster unavailable.</p>
      )}
    </div>
  )
}

export default TeamRoster
