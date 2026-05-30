# VCT Match Predictor

**Data-driven Valorant Champions Tour match forecasting** — pick any two pro teams, get a Random Forest winner prediction, per-map breakdowns, stat comparisons, and roster intel in a polished dark UI.

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Random%20Forest-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

Forked from [terrdv/VCT-Match-Predictor](https://github.com/terrdv/VCT-Match-Predictor) and extended with a Kaggle data pipeline, 2021–2026 seasons, tuned feature engineering, map-level models, and a full UI redesign.

---

## What it does

1. **Select two VCT teams** from 74 pro rosters with logos and region tags.
2. **Get a match winner prediction** with confidence tier (Likely · Slight edge · Toss-up), animated reveal, and a highlighted predicted winner strip.
3. **Drill into four detail tabs** — map-by-map odds, head-to-head stats, full breakdown with key factors, and live rosters.

Shareable URLs: `/predict/Sentinels/Fnatic` (team names are URL-encoded automatically).

---

## Screens & features

### Home
- Dual team dropdowns with search-friendly labels
- Matchup preview cards once both teams are selected
- One-click navigation to the prediction view

### Prediction page

| Area | What you get |
|------|----------------|
| **Winner strip** | Side-by-side team cards, gold “Predicted” badge, shimmer border, and glow on the favored team |
| **Confidence badge** | Likely / Slight edge / Toss-up based on model margin |
| **Map Predictions** | All 12 standard maps (A–Z), Valorant splash art, per-map win %, favored team logo |
| **Stats** | H2H win rates, Recharts comparison chart, metrics table with leader logos on each delta |
| **Breakdown** | Full winner analysis, win probabilities, and “why this team is favored” key factors |
| **Roaster** | Player rosters lazy-loaded from the VLR API when you open the tab |

### About
- Dataset attribution and live model accuracy from `model_metrics.json`
- Sample past predictions with hit/miss markers

---

## Model accuracy

Refresh metrics anytime:

```bash
cd server
python scripts/evaluate_model.py
```

| Metric | Value | Meaning |
|--------|------:|---------|
| Random split | **73.4%** | Stratified 80/20 holdout with tuned Random Forest |
| Time-ordered split | **69.7%** | Train on earlier matches, test on later ones |
| Deployed holdout | **76.9%** | Saved `rf.pkl` evaluated on last 20% of augmented rows |

> **Read this carefully:** Features use full historical win rates and head-to-head stats (not point-in-time). Offline accuracy is optimistic vs true pre-match forecasting. Treat **~70%** (time-ordered) as the realistic ballpark.

| | |
|---|---|
| **Algorithm** | `RandomForestClassifier` via `RandomizedSearchCV` |
| **Features** | 14 base stats + 7 delta features (Team A − Team B) → **21 total** |
| **Training** | Order-invariant augmentation (swap teams + flip label) |
| **Map model** | Separate map win % from `map_team_stats.csv` / `map_h2h_stats.csv` |
| **Inputs** | H2H win rate, overall win rate, K/D, damage, ACS, first kills/deaths |

**Dataset:** [Valorant Champion Tour 2021–2026 — Ryan Luong (Kaggle)](https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data)

Raw Kaggle files (~79 MB) are not committed. Download into `server/data/kaggle/` with `update_dataset.py --download`.

---

## Quick start

### Prerequisites

- Python **3.10+**
- Node.js **18+**
- [Kaggle API credentials](https://www.kaggle.com/docs/api) (only for `--download`)

### Install

```bash
git clone https://github.com/maharshinath/VCT-Match-Predictor.git
cd VCT-Match-Predictor

cd server && pip install -r requirements.txt
cd ../client && npm install
```

### Build dataset & model (first run)

```bash
cd server
python scripts/update_dataset.py --download
```

Generates `csv/*.csv`, map stats, and `models/rf.pkl`.

### Run locally

**API** (port **5001** — avoids Windows conflicts on 5000):

```bash
cd server
python -c "from app import app; app.run(debug=True, port=5001, use_reloader=False)"
```

**Frontend:**

```bash
cd client
npm run dev
```

| Service | URL |
|---------|-----|
| App | http://localhost:5173 |
| API | http://127.0.0.1:5001/api |

Restart Flask after retraining so it loads the new `rf.pkl`.

### Tests

```bash
cd server
python -m pytest tests/test_api.py -q
```

---

## API

Base URL: `http://127.0.0.1:5001/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/teams` | All teams (stats + logo paths) |
| `GET` | `/info/<team>` | Single team row |
| `GET` | `/predict/<team1>/<team2>` | Winner %, map predictions (×12), key factors, confidence |
| `GET` | `/matchup_data/<team1>/<team2>` | Feature row for stat comparison |
| `GET` | `/roster/<team>` | Players and coaches (VLR, cached) |
| `GET` | `/meta` | Comp pool, `model_metrics` |

---

## Project structure

```
VCT-Match-Predictor/
├── client/
│   ├── src/
│   │   ├── pages/              # Home, Prediction, About
│   │   ├── components/         # Prediction, MapPredictions, TeamDashboard, TeamRoster
│   │   ├── data/mapImages.js   # Valorant map splash URLs (valorant-api.com)
│   │   └── services/api.js
│   └── package.json
├── server/
│   ├── app.py                  # Flask REST API
│   ├── model_training.py       # Feature engineering + hyperparameter tuning
│   ├── map_predictions.py      # Per-map win probabilities
│   ├── prediction_extras.py    # Confidence, key factors, map sort
│   ├── roster.py               # VLR roster cache
│   ├── models/rf.pkl           # Trained model (generated)
│   ├── scripts/
│   │   ├── update_dataset.py   # Rebuild CSVs + retrain
│   │   └── evaluate_model.py   # Refresh model_metrics.json
│   ├── data/model_metrics.json
│   └── tests/test_api.py
└── .github/workflows/          # Optional weekly data refresh
```

---

## Updating data

From `server/`:

```bash
python scripts/update_dataset.py --download   # fetch latest Kaggle zip
python scripts/update_dataset.py              # rebuild CSVs + retrain RF
python scripts/evaluate_model.py              # refresh About-page metrics
```

| Flag | Effect |
|------|--------|
| `--download` | Fetch Kaggle zip before processing |
| `--min-year 2024` | Seasons from 2024 onward only |
| `--all-years` | All seasons including Challengers |

Default: **`--min-year 2021`** with pro-tournament filtering (Champions, Masters, `VCT YYYY:` events).

---

## Tech stack

| Layer | Technologies |
|-------|--------------|
| Frontend | React 19, React Router 7, Vite 7, Recharts |
| Backend | Flask 3, Flask-RESTful, flask-cors |
| ML / data | scikit-learn, pandas, joblib |
| Rosters | [VLR API](https://vlr.orlandomm.net/) |
| Map art | [valorant-api.com](https://valorant-api.com) CDN |

---

## Roadmap

- Point-in-time features to reduce train/test leakage
- Gradient boosting (XGBoost / LightGBM) with proper tuning
- Recent form and roster strength as model inputs
- Self-hosted map images

---

## License & credits

- **Dataset:** MIT (Kaggle)
- **Application code:** see repository license
- **Author:** [maharshinath](https://github.com/maharshinath)
- **Original fork:** [terrdv/VCT-Match-Predictor](https://github.com/terrdv/VCT-Match-Predictor)
