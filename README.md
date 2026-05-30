# VCT Match Predictor

Full-stack web app that predicts winners of **Valorant Champions Tour (VCT)** matches using a **Random Forest** classifier trained on official pro match and player statistics.

**Live stack:** React (Vite) frontend · Flask REST API · scikit-learn model

Forked from [terrdv/VCT-Match-Predictor](https://github.com/terrdv/VCT-Match-Predictor), extended with an automated Kaggle data pipeline, expanded dataset (2021–2026), UI/API fixes, and a retrained model.

---

## Features

- **Match predictions** — pick two teams and get a predicted winner with team logos
- **76 VCT teams** in the dropdown (Champions, Masters, Kickoff, Stage events)
- **14 input features** per matchup: head-to-head winrate, overall winrate, K/D, damage, combat score, first kills, first deaths
- **Dataset rebuild script** — download from Kaggle, process CSVs, and retrain `rf.pkl` in one command
- **Team logos** served from Flask static assets
- **CORS-enabled API** for local development

---

## Model & data

| Item | Details |
|------|---------|
| **Algorithm** | `RandomForestClassifier` (100 trees, `max_depth=10`) |
| **Training** | Order-invariant augmentation (swap Team A/B + flip label) |
| **Split** | 80% train / 20% test, `random_state=42` |
| **Training accuracy** | ~85.5% |
| **Test accuracy** | ~72.8% |
| **Matches in dataset** | 865 pro VCT matches |
| **Oldest events** | 2021 (Champions 2021, Masters Reykjavík / Berlin, etc.) |
| **Newest events** | 2026 (VCT Kickoffs, Masters Santiago 2026) |

**Data source:** [Valorant Champion Tour 2021–2026 — Ryan Luong (Kaggle)](https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data)

Raw Kaggle files are **not** committed (~79 MB). They are downloaded into `server/data/kaggle/` via the update script.

**Note:** Head-to-head and winrates are computed from full match history (not point-in-time), so offline accuracy is optimistic vs true pre-match forecasting. See *Possible improvements* below.

---

## Project structure

```
VCT-Match-Predictor/
├── client/                 # React + Vite frontend
│   └── src/
│       ├── pages/          # MakePrediction, PredictionPage, About
│       ├── components/     # Matchup, Prediction, TeamCard, …
│       └── services/api.js   # API client (port 5001)
├── server/
│   ├── app.py              # Flask REST API
│   ├── models/
│   │   ├── RandomForestPredictor.py
│   │   └── rf.pkl          # Trained model (generated)
│   ├── csv/
│   │   ├── scores.csv      # Match results (generated)
│   │   ├── team_data.csv   # Team aggregates (generated)
│   │   └── filtered_matches.csv
│   ├── scripts/
│   │   └── update_dataset.py
│   ├── static/logos/       # Team logo images
│   └── data/kaggle/        # Raw Kaggle data (gitignored)
└── README.md
```

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/teams` | All teams with stats and logo paths |
| `GET` | `/api/info/<team>` | Single team row |
| `GET` | `/api/predict/<team1>/<team2>` | Predicted winner (`team1_win_prediction`) |
| `GET` | `/api/matchup_data/<team1>/<team2>` | Feature row used for prediction |

Default base URL: `http://127.0.0.1:5001/api`

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- [Kaggle API credentials](https://www.kaggle.com/docs/api) (for `--download` only)

### 1. Clone and install

```bash
git clone https://github.com/maharshinath/VCT-Match-Predictor.git
cd VCT-Match-Predictor

# Backend
cd server
pip install -r requirements.txt

# Frontend (new terminal)
cd client
npm install
```

### 2. Build dataset & model (first time)

From `server/`:

```bash
python scripts/update_dataset.py --download
```

This downloads Kaggle data, builds `csv/*.csv`, and trains `models/rf.pkl`.

### 3. Run the app

**Backend** (from `server/`):

```bash
python -c "from app import app; app.run(debug=True, port=5001, use_reloader=False)"
```

**Frontend** (from `client/`):

```bash
npm run dev
```

Open **http://localhost:5173/** — API at **http://127.0.0.1:5001**

> Port **5001** is used because port 5000 is often occupied locally. The frontend is configured for `5001` in `api.js` and logo URLs.

---

## Updating the dataset

From `server/`:

```bash
# Refresh from Kaggle (optional)
python scripts/update_dataset.py --download

# Rebuild CSVs + retrain model (default: 2021+ pro VCT events)
python scripts/update_dataset.py
```

**Script options:**

| Flag | Effect |
|------|--------|
| `--download` | Fetch latest zip from Kaggle before processing |
| `--min-year 2024` | Only include seasons from 2024 onward |
| `--all-years` | Include all seasons (includes Challengers; many extra teams) |

Default: **`--min-year 2021`** with pro-tournament filtering (Champions, Masters, `VCT YYYY:` events).

---

## Recent changes

- Added `server/scripts/update_dataset.py` — Kaggle → CSV → model pipeline
- Expanded data to **2021–2026** (865 matches, 76 teams)
- Retrained Random Forest with order-invariant augmentation
- Fixed API JSON responses (`to_dict` instead of double-encoded strings)
- Fixed empty team dropdowns (option styling + API error handling)
- Pointed frontend/API to **port 5001**
- Updated About page (Random Forest, accuracy, dataset link)
- Added root `.gitignore` (excludes `node_modules`, `data/kaggle/`)
- Restored team logos under `server/static/logos/`

---

## Possible improvements

- Time-based train/test split and point-in-time features (reduce leakage)
- Order-invariant inference (score both team orderings at predict time)
- Recent-form features (last N matches)
- Gradient boosting (XGBoost / LightGBM) with hyperparameter tuning
- Map/agent features from additional Kaggle CSVs

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| Frontend | React 19, React Router 7, Vite 7 |
| Backend | Flask 3, Flask-RESTful, flask-cors |
| ML | scikit-learn, pandas, joblib |

---

## License

Dataset: MIT (Kaggle). Application code: see repository license.

---

## Author

[maharshinath](https://github.com/maharshinath) — fork of [terrdv/VCT-Match-Predictor](https://github.com/terrdv/VCT-Match-Predictor)
