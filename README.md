# DayPlan: Smart Travel Planner

Plan a trip, see what is *on the way*, find places beyond the famous ones, and budget it.
React (Vite + Tailwind + Leaflet) frontend, Flask + SQLAlchemy + SQLite backend.
Live data comes from free, keyless APIs (Nominatim, OSRM, Open-Meteo, Overpass). Curated
local CSV datasets back them up, so a slow or dead public server does not empty the page.

## Features

| Feature | What it does |
|---|---|
| Plan a trip | One request (`POST /api/plan-trip`) returns route, weather, attractions, hotels, restaurants, budget and itinerary |
| Destination | Tourist attractions near the destination, nearest first (live + curated) |
| Highlights | Hidden / authentic spots, with hotels and restaurants filtered out of the list |
| **On the Way** | Stops along the driving route (see "Along-the-route stops"), shown as a numbered timeline **and** as numbered markers on the existing Map tab |
| Hotels | Live OpenStreetMap hotels. An honest "unavailable" message if the live lookup failed |
| Restaurants | Live + curated, with a veg / non-veg / both filter |
| Weather, Budget, Itinerary | Open-Meteo forecast, a budget breakdown, a deterministic day-by-day plan |
| Accounts | Register / login (JWT), saved trips and favourites |

Star ratings are shown only when the data really contains them. Nothing is invented.

## Resilience design

Every external call is independent. A failure degrades one section, never the whole request.

| Section | Live source | Fallback | If both fail |
|---|---|---|---|
| Route | OSRM | none | route is `null`, rest of plan still renders |
| Weather | Open-Meteo | none | `null` |
| Attractions | Overpass | curated tourist spots (459) | empty list |
| Restaurants | Overpass | curated restaurants (143 rows) | empty list |
| Highlights | Overpass | curated spots | empty list |
| Along the route | Overpass (route search) | curated spots near the route | `[]` plus an honest empty state |
| Hotels | Overpass | **none yet** (dataset in progress) | `hotelsStatus: "unavailable"` |

Rules that apply across the services:

- **Blend, don't replace.** If live results number fewer than 5, curated rows are added to them
  instead of swapping the whole list.
- **Fail-fast cooldown.** After an Overpass outage the app stops calling it for 120 s, so one
  dead server does not make every request wait for a timeout.
- **Silent failures are treated as failures.** Overpass can answer HTTP 200 with an empty list and
  a `runtime error` remark when it is overloaded. That is raised as an error, not read as
  "no results".
- Route searches never start the global cooldown (`trip_cooldown=False`).
- Failures are logged server-side with Python `logging`.

## Along-the-route stops

Implemented in `services/corridor_service.py` and `utils/geo.py`.

1. The OSRM route is loaded into a `RouteIndex`. It projects points onto a local flat map and
   computes, for any spot, its distance off the route and its distance along the route (km).
2. Candidates are all curated spots plus live OpenStreetMap places. Only spots within
   **5 km** of the route are kept. The first and last **10 km** are skipped, because those are
   the origin and destination themselves.
3. Hotels and restaurants are excluded (`EXCLUDED_TAGS`).
4. Live and curated duplicates are merged (same normalised name, or under 0.25 km apart).
5. The route is cut into 15 equal stretches, with at most 2 stops per stretch. This stops one
   city from supplying all the stops. Curated spots come first within a stretch. Results are
   ordered by distance along the route.
6. Live route query: the route is thinned to one waypoint about every 4 km, sent in pieces of 50
   points, with at most 6 queries and a 30 s time budget. If the first query fails, the error is
   raised. If a later one fails, the partial result is kept.

## Project structure

```
DAYPLAN_CSV/
|-- backend/
|   |-- app.py                    App factory (loads CSV datasets at startup)
|   |-- config.py                 Environment-driven configuration
|   |-- requirements.txt
|   |-- data/dataset1, dataset2   Curated CSVs
|   |-- database/                 SQLAlchemy models
|   |-- routes/                   Thin controllers, one blueprint per resource
|   |-- services/
|   |   |-- overpass_service.py   Overpass client, cooldown, remark detection, route search
|   |   |-- corridor_service.py   Along-the-route selection
|   |   |-- local_data_service.py CSV loading + nearby lookups
|   |   |-- destination_service.py, restaurant_service.py, highlight_service.py
|   |   |-- osrm_service.py, weather_service.py, geocoding_service.py
|   |   +-- budget_service.py, ai_service.py
|   |-- utils/geo.py              haversine, RouteIndex
|   |-- scripts/                  geocode_restaurant_csvs.py + diagnostics (below)
|   +-- tests/                    pytest suite (96 tests)
+-- frontend/src/
    |-- api/  components/  context/
    +-- pages/                    One component per route (RouteHighlights, MapPage, ...)
```

## Running it

Backend:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py                      # http://localhost:5000
```

Frontend:

```powershell
cd frontend
npm install
copy .env.example .env             # set VITE_API_URL
npm run dev                        # http://localhost:5173
```

The SQLite database is created on first run.

## Tests

```powershell
cd backend
pip install pytest
python -m pytest tests -q          # 96 tests
```

`pytest` is not in `requirements.txt` (it is a development tool). Tests use `monkeypatch` fakes
for Overpass and OSRM, so they run offline and never hit a public server.

## Diagnostic scripts (`backend/scripts`)

| Script | Use |
|---|---|
| `check_overpass.py` | Is Overpass answering a tiny query, and how fast? Run this first |
| `check_route_query.py` | Tries the real route query and prints the server's `remark` if any |
| `check_corridor.py` | Runs the corridor selection on a saved `route.json` |

The two route scripts need a saved route first:
`$r.route | ConvertTo-Json -Depth 10 -Compress | Out-File -Encoding utf8 route.json`.
Delete `route.json` afterwards and never `git add` it.

## API endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/plan-trip` | Full plan (includes `routeHighlights`, `hotels`, `hotelsStatus`) |
| `GET /api/destination`, `/api/highlights`, `/api/hotels`, `/api/restaurants` | Per-section data |
| `GET /api/route`, `/api/transport`, `/api/weather` | Route, transport options, weather |
| `POST /api/budget`, `/api/itinerary` | Budget and itinerary |
| `GET /api/local-attractions?city=`, `/api/trending?limit=` | Curated datasets |
| `POST /api/register`, `/api/login`, `GET /api/profile` | Auth |
| `POST/GET /api/trips`, `DELETE /api/trips/<id>` | Saved trips |
| `POST/GET /api/favorites`, `DELETE /api/favorites/<id>` | Favourites |

## Datasets

- 459 curated tourist spots across 13 Indian cities, 30 famous global landmarks.
- 143 curated restaurant / hidden-spot rows, of which 69 (48%) are geocoded. Ungeocoded rows
  cannot be placed by distance.
- Hotel dataset: **in progress**. Only sourced rows with a source URL will be added.

### Data-integrity lesson: pandas and the string "NA"

`pandas.read_csv()` turns the text `NA` into `NaN` by default. The `VegStatus` column uses `NA` on
purpose (no diet tag), and `jsonify()` then writes the invalid JSON token `NaN`, which breaks
`JSON.parse()` in the browser. Fixed with `keep_default_na=False, na_values=['']` in
`local_data_service.py`. Missing coordinates are also sanitised before building any response.

## Known limitations

- **Overpass reliability.** The public servers were timing out during development. The live
  route search has so far been tested only against simulated servers, not a healthy real one.
- **Sparse corridor data.** Without live data, a route may have few curated stops (Hyderabad to
  Munnar gave 1).
- **No offline hotel fallback yet.** Hotels depend entirely on live data until the dataset is added.
- Transport options are a heuristic, and the itinerary is generated deterministically.

## Deployment

- **Frontend (Vercel):** set `VITE_API_URL` to the backend URL, build `npm run build`, output `dist`.
- **Backend (Render):** set `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS`. Start command: `gunicorn app:app`.
