
import '../css/Home.css'

function About() {


    return (

    <div className="home">
        <div className="text-content">
            <h1>About</h1>
            <div className="about">
                <p>
                    My machine learning algorithm analyzes comprehensive team statistics including win rates, K/D ratios, damage per round, combat scores, and first blood percentages to predict the outcomes of Valorant Champions Tour matches. 
                    By processing historical performance data and current team form, my tool provides data-driven predictions to help fans and analysts understand which team has the statistical advantage going into each match.
                    <br />
                    <br></br>
                    This website uses a Random Forest model to make predictions, trained on this Kaggle dataset: 
                    <a href="https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data" target="_blank" rel="noopener noreferrer">
                     Valorant Champion Tour 2021-2026 Data by Ryan Luong
                    </a> 
                    <br />
                    <br />
                    Model test accuracy (held-out split): ~73%
                    <br />
                    <br />
                    Data last updated: 2026/05/31
                </p>
                
            </div>
            <br></br>
            <h2>Past Predictions</h2>
            <div className="preds">
                <p>Valorant Masters Toronto 2025 June 17th: Gen.G vs G2 ✅</p>
                <p>Valorant Masters Toronto 2025 June 17th: Sentinels vs Fnatic ✅</p>
                <p>Valorant Masters Toronto 2025 June 20th: Paper Rex vs Wolves ✅</p>
                <p>Valorant Masters Toronto 2025 June 20th: G2 vs Fnatic ❌</p>
                <p>Valorant Masters Toronto 2025 June 21st: Wolves vs Fnatic ✅</p>
                <p>Valorant Masters Toronto 2025 June 22nd: Paper Rex vs Fnatic ✅</p>
            </div>
            

        </div>
    </div>
    )
}


export default About