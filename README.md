# DayPlan — AI Smart Travel Planner

A full-stack travel planning app: React (Vite + Tailwind) frontend, Flask REST API backend,
SQLite database, and **only free, keyless APIs** (OpenStreetMap / Nominatim, OSRM, Open-Meteo,
Overpass).

## Project Structure

```
dayplan/
├── backend/          Flask REST API
│   ├── app.py         App factory & entrypoint
│   ├── config.py       Environment-driven configuration
│   ├── database/        SQLAlchemy models
│   ├── routes/         Thin controllers (one blueprint per resource)
│   ├── services/        All external API integrations & business logic
│   └── utils/          Validators & centralized error handling
└── frontend/          React + Vite + Tailwind app
    └── src/
        ├── api/          Axios client
        ├── components/    Navbar, Footer, shared UI, TripTabs
        ├── context/      Auth + Trip state
        └── pages/        One component per route
```

## Running the Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit secrets as needed
python app.py                   # runs on http://localhost:5000
```

The SQLite database (`dayplan.db`) and all tables are created automatically on first run.

## Running the Frontend

```bash
cd frontend
npm install
cp .env.example .env            # points VITE_API_URL at your backend
npm run dev                     # runs on http://localhost:5173
```

## Key Flow

1. **Home** → "Plan My Trip" → **Planner** (origin, destination, people, days, budget, preference)
2. Planner calls `POST /api/plan-trip`, which orchestrates geocoding, routing, attractions,
   hotels, restaurants, weather, budget, and itinerary generation in one request.
3. Results are stored in `TripContext` and shown across the **Destination / Transportation /
   Map / Hotels / Restaurants / Weather / Budget / Itinerary** tabs.
4. Logged-in users can **Save Trip** (stored per-user) and revisit it under **Saved Trips**.

## APIs Used (all free, no API key required)

| Purpose      | Provider                          |
|--------------|------------------------------------|
| Geocoding    | OpenStreetMap Nominatim            |
| Routing      | OSRM (Open Source Routing Machine) |
| Weather      | Open-Meteo                         |
| Hotels/Food/Attractions | Overpass API (OpenStreetMap) |
| Maps         | Leaflet.js + OpenStreetMap tiles   |

## Deployment

- **Frontend** → Vercel: set `VITE_API_URL` to your deployed backend URL as an environment variable, build command `npm run build`, output dir `dist`.
- **Backend** → Render: set `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS` (your Vercel URL) as environment variables. Start command: `gunicorn app:app`.

## Notes

- Nominatim/Overpass have usage limits and rate-limiting for heavy traffic — for production
  scale, consider self-hosting or a caching layer.
- Transport (flight/train/bus) availability and costs are **heuristic estimates** based on
  distance, since no free, keyless API exposes live schedules — this is clearly labeled in the UI.
- The AI Itinerary is a deterministic planner built from real nearby-attraction data; the
  service is structured so a real LLM call can be swapped in without touching routes.
