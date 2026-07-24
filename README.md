# DayPlan — AI Smart Travel Planner

A full-stack travel planning app: React (Vite + Tailwind) frontend, Flask REST API backend,
SQLite database, **free keyless live APIs** (OpenStreetMap / Nominatim, OSRM, Open-Meteo,
Overpass) blended with **curated local CSV datasets** as a resilience layer and standalone
feature source.

## What's in this project

- Live trip planning (route, weather, attractions, hotels, restaurants, budget, AI itinerary)
  sourced from free OpenStreetMap-ecosystem APIs.
- A **local dataset layer** (`backend/data/`) covering ~460 curated Indian tourist spots and
  30 globally famous landmarks, wired into the backend as:
  - **A fallback** — if the live Overpass API returns too little (or fails/times out), the
    app blends in curated local attractions instead of showing an empty page, computing real
    distances with the same haversine logic used for live results.
  - **A feature** — `/api/trending` surfaces the most-visited famous landmarks worldwide,
    independent of any live API call.
- **Graceful degradation**: every external API call in the main planning flow (Overpass ×3,
  OSRM, Open-Meteo) is individually fault-tolerant. If one service is temporarily unavailable,
  the rest of the trip plan still renders instead of the whole request failing.

## Project Structure

```
dayplan/
├── backend/          Flask REST API
│   ├── app.py                  App factory & entrypoint (loads CSV datasets at startup)
│   ├── config.py                Environment-driven configuration
│   ├── data/                   Local CSV datasets (curated attractions, famous places)
│   ├── database/                 SQLAlchemy models
│   ├── routes/                  Thin controllers (one blueprint per resource)
│   ├── services/
│   │   ├── local_data_service.py   Loads/serves the CSV datasets from memory
│   │   ├── destination_service.py  Live + local attraction merge, fallback, sorting
│   │   └── ...                    Other external API integrations & business logic
│   └── utils/                   Validators, geo math (haversine), centralized error handling
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
| Hotels/Food/Attractions | Overpass API (OpenStreetMap), backed by local CSV fallback |
| Maps         | Leaflet.js + OpenStreetMap tiles   |

## Local Dataset Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/local-attractions?city=<name>` | Curated attractions for one of 13 pre-loaded Indian cities |
| `GET /api/trending?limit=<n>` | Top N globally famous landmarks by annual visitor count |

## Resilience Design

Rather than a single all-or-nothing API call, `POST /api/plan-trip` treats each external
dependency independently:

- **Attractions**: tries Overpass first; if it returns fewer than 5 results (or fails
  entirely), curated CSV spots are blended in and the combined list is sorted by real
  distance from the destination.
- **Hotels / Restaurants / Route / Weather**: each wrapped individually, so a single failed
  service degrades that one section of the response (empty list / `null`) instead of
  failing the whole request. All failures are logged server-side via Python's `logging`
  module for visibility during development.

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