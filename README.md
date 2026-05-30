# VALORANT Champions Tour (VCT) Match Predictor

Predict the outcome of official VCT matches using Random Forest.

## Tech Stack

### Frontend
- **React**
- **Vite**

### Backend
- **Flask (Python)**

---

## Features

- Predicts VCT match winners based on team statistics and historical data using a random forest classifier

---

## Setup
```bash
git clone <repository-url>
cd VCT-Match-Predictor-main

# Backend setup
cd server
pip install -r requirements.txt
python scripts/update_dataset.py --download   # first time: fetch Kaggle data + train model
python -c "from app import app; app.run(debug=True, port=5001, use_reloader=False)"

# Frontend setup in second terminal
cd client
npm install
npm run dev
```

Open http://localhost:5173/ (API runs on http://127.0.0.1:5001).

## Updating the dataset

From `server/`:

```bash
python scripts/update_dataset.py --download   # optional: refresh from Kaggle
python scripts/update_dataset.py              # rebuild csv/ + rf.pkl (2024–2026 VCT by default)
```

Data source: [Valorant Champion Tour 2021–2026 (Ryan Luong)](https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data)









