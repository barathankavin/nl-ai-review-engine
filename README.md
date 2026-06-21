# NL - AI Review Engine

Natural Language AI Review Engine project.

## Review Discovery Engine (frontend)

React dashboard that reads scraped Spotify Google Play reviews from the Google Sheet synced by the n8n workflow (**NL Spotify review Scrapped data**).

### Run locally

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api/reviews.csv` to the Google Sheet CSV export.

### Configuration

Copy `frontend/.env.example` to `frontend/.env` if needed. Defaults point at sheet `1BL-09eLm61Zy3OLFxxqQVLf-I148dC30qbaKWa618wI`.

For production builds without the Vite proxy, set `VITE_REVIEWS_CSV_URL` to the public CSV export URL (sheet must be shared as “Anyone with the link can view”).

### Features

- Live sync from Google Sheets (same columns as the n8n workflow)
- Search, rating filters, developer reply filter, sorting
- Stats: average rating, distribution, reply rate
- Review cards with Play Store links and Spotify responses
