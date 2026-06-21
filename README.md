# NL - AI Review Engine

Natural Language AI Review Engine project.

## Review Discovery Engine

Full-stack review discovery: **n8n** → Google Sheets → Python pipeline → React UI with **Groq** chat.

Design system: `frontend/src/styles/design-system.css` (Spotify-inspired tokens).

### Run locally

```bash
# Backend
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Open http://127.0.0.1:5173 — Vite proxies `/api/v1` to the backend.

### Deploy on Railway (recommended)

Deploy **two services** from this monorepo in one Railway project.

#### 1. Backend — `review-engine-api`

| Setting | Value |
|---------|--------|
| Root directory | `backend` |
| Builder | Dockerfile (`backend/Dockerfile`) |
| Health check | `/api/v1/health` |

**Environment variables**

| Variable | Required | Example |
|----------|----------|---------|
| `GROQ_API_KEY` | Yes | From [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` |
| `DATABASE_URL` | No | `sqlite:////app/data/reviews.db` (default in Docker) |
| `PYTHONPATH` | No | `/app` |
| `FRONTEND_URL` | No | `https://your-frontend.up.railway.app` |

**Volume (recommended):** mount `/app/data` so SQLite survives redeploys.

Generate a public domain for the API, e.g. `https://review-engine-api-production.up.railway.app`.

#### 2. Frontend — `review-engine-web`

| Setting | Value |
|---------|--------|
| Root directory | `frontend` |
| Builder | Dockerfile (`frontend/Dockerfile`) |

**Environment variables**

| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_BASE_URL` | Yes | `https://review-engine-api-production.up.railway.app/api/v1` |

Use Railway variable references after the backend service exists:

```text
VITE_API_BASE_URL=https://${{review-engine-api.RAILWAY_PUBLIC_DOMAIN}}/api/v1
```

Replace `review-engine-api` with your backend service name if different.

Generate a public domain for the frontend. Set `FRONTEND_URL` on the backend to that URL.

#### 3. Data flow (n8n + Groq)

```text
n8n (Apify scrape) → Google Sheet
        ↓
Backend ingest (/api/v1/refresh) + GitHub Actions Pipeline Refresh
        ↓
SQLite on Railway volume → Groq chat + pattern UI
```

- **n8n** keeps writing reviews to the Google Sheet (no Railway change needed).
- **Groq** runs on the Railway backend via `GROQ_API_KEY`.
- **Scheduled refresh:** GitHub Actions → **Pipeline Refresh** (add `GROQ_API_KEY` repo secret), or click **Sync data** in the UI.

#### Verify deployment

1. `GET https://<api-domain>/api/v1/health` → `groq_enabled: true`, `pipeline_ml_available: true`
2. Open the frontend URL → patterns load after first pipeline refresh
3. Chat panel answers with Groq

### Docker (local / self-hosted)

```bash
cd backend
docker build -t review-engine-api .
docker run -p 8000:8000 --env-file .env review-engine-api
```

See `architecture.md` for full system design.
