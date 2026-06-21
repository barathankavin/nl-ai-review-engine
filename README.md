# NL - AI Review Engine

Natural Language AI Review Engine project.

## Review Discovery Engine

Full-stack review discovery: n8n → Google Sheets → Python pipeline → React UI with Groq chat.

Design system: `frontend/src/styles/design-system.css` (Spotify-inspired tokens).

### Run locally

```bash
# Backend
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

### Deploy

**Vercel (frontend + backend, recommended)**

This repo uses Vercel **Services** (`experimentalServices` in root `vercel.json`):

| Service | Path | Entry |
|---------|------|-------|
| Frontend (Vite) | `/` | `frontend/` |
| Backend (FastAPI) | `/_/backend` | `backend/app/main.py` |

1. Import the GitHub repo in [Vercel](https://vercel.com).
2. Set **Framework Preset** to **Services** (Project Settings → Build & Deployment).
3. Add environment variables:
   - `GROQ_API_KEY` — Groq API key (enables chat + theme labeling)
   - `GROQ_MODEL` — optional, default `llama-3.3-70b-versatile`
   - `DATABASE_URL` — optional on Vercel; defaults to `sqlite:////tmp/reviews.db`
4. Deploy. The frontend calls the API at `/_/backend/api/v1` on the same domain.

Health check URL: `https://<your-domain>/_/backend/api/v1/health`

**Vercel bundle limits:** the backend uses a lightweight `pyproject.toml` (no `sentence-transformers` / clustering). Pipeline refresh on Vercel returns 503 — run **Pipeline Refresh** via GitHub Actions or deploy the full backend on Railway/Docker. Chat still works via Groq with keyword-based review retrieval.

Local multi-service preview:

```bash
npx vercel dev -L
```

**Backend only (Docker / Render / Railway)**

```bash
cd backend
docker build -t review-engine-api .
docker run -p 8000:8000 --env-file .env review-engine-api
```

For split hosting, set frontend `VITE_API_BASE_URL` to your backend URL + `/api/v1`.

See `architecture.md` for full system design.
