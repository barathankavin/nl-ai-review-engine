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

**Frontend (Vercel / Netlify)**
```bash
cd frontend
npm run build
```
- Root directory: `frontend`
- Build command: `npm run build`
- Output: `dist`
- Set `VITE_API_BASE_URL` to your deployed backend URL + `/api/v1`

**Backend (Docker / Render / Railway)**
```bash
cd backend
docker build -t review-engine-api .
docker run -p 8000:8000 --env-file .env review-engine-api
```

See `architecture.md` for full system design.
