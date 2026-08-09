# Deploy on Render

Live setup uses **two** Render services (reliable on the free tier):

1. **Web Service (Python)** — Flask API (`server/`)
2. **Static Site** — React build (`client/`)

## Steps (Dashboard)

1. Create / log into [Render](https://render.com) and connect the **maharshinath** GitHub account.
2. **New → Blueprint** → pick `maharshinath/VCT-Match-Predictor` (reads `render.yaml`).
3. When prompted for `VITE_API_ORIGIN` on the static site, set it to your API URL **without a trailing slash**, e.g.  
   `https://vct-match-predictor-api.onrender.com`  
   (use the exact hostname Render assigns after the API service is created — you can create the API first, then set this and redeploy the static site).
4. Deploy. First API boot loads the model (can take 1–3 minutes). Free API instances **sleep** when idle; the first hit afterward is slow.

### Manual (no Blueprint)

**API**

- Root directory: `server`
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
- Health check: `/api/health`

**Static site**

- Root directory: `client`
- Build: `npm install && npm run build`
- Publish: `dist`
- Env: `VITE_API_ORIGIN=https://YOUR-API.onrender.com`
- SPA rewrite: `/*` → `/index.html`

## Single-service option

If you prefer one URL only, build the client into `client/dist` and serve it from Flask (supported in `app.py` when `dist` exists). That needs a Docker image with both Python and Node — use the two-service Blueprint above on free tier unless you add a `Dockerfile`.

## Local production smoke-test

```bash
cd client && set VITE_API_ORIGIN=http://127.0.0.1:5001 && npm run build
cd ../server && gunicorn app:app --bind 127.0.0.1:5001
```
