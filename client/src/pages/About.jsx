import { useEffect, useState } from 'react'
import { getMeta } from '../services/api'
import '../css/Home.css'

const PAST_PREDS = [
    { match: 'Masters Toronto · Jun 17', teams: 'Gen.G vs G2', ok: true },
    { match: 'Masters Toronto · Jun 17', teams: 'Sentinels vs Fnatic', ok: true },
    { match: 'Masters Toronto · Jun 20', teams: 'Paper Rex vs Wolves', ok: true },
    { match: 'Masters Toronto · Jun 20', teams: 'G2 vs Fnatic', ok: false },
    { match: 'Masters Toronto · Jun 21', teams: 'Wolves vs Fnatic', ok: true },
    { match: 'Masters Toronto · Jun 22', teams: 'Paper Rex vs Fnatic', ok: true },
]

function About() {
    const [meta, setMeta] = useState(null)

    useEffect(() => {
        getMeta().then(setMeta).catch(() => {})
    }, [])

    const metrics = meta?.model_metrics

    return (
        <div className="home about-page">
            <header className="text-content">
                <p className="section-eyebrow">About this project</p>
                <h1>About</h1>
            </header>

            <div className="about">
                <p>
                    This app predicts VCT match and map winners using a Random Forest trained on
                    pro match stats — win rates, K/D, damage, ACS, first kills/deaths, and map history.
                    Map predictions cover all 12 standard Valorant maps.
                </p>
                <p>
                    Dataset:{' '}
                    <a
                        href="https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Valorant Champion Tour 2021–2026 (Kaggle)
                    </a>
                </p>
                {metrics && (
                    <p>
                        Model accuracy — random split: {metrics.random_split_accuracy}%
                        {metrics.time_ordered_split_accuracy != null && (
                            <> · time-ordered split: {metrics.time_ordered_split_accuracy}%</>
                        )}
                        . The time-ordered figure is a better proxy for real forecasting.
                    </p>
                )}
            </div>

            <section className="about-predictions">
                <h2>Past predictions</h2>
                <ul className="preds-list">
                    {PAST_PREDS.map((p) => (
                        <li key={`${p.match}-${p.teams}`}>
                            <span>
                                <strong>{p.match}</strong> — {p.teams}
                            </span>
                            <span className={p.ok ? 'result-ok' : 'result-miss'}>
                                {p.ok ? '✓' : '✗'}
                            </span>
                        </li>
                    ))}
                </ul>
            </section>
        </div>
    )
}

export default About
