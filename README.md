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
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> function N($s){ $s.Replace("`r`n","`n") }
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> function Patch($path, $old, $new){
>>   $t = N (Get-Content $path -Raw)
>>   $o = N $old
>>   if (-not $t.Contains($o)) { Write-Host "NOT FOUND in $path" -ForegroundColor Red; return }
>>   $i = $t.IndexOf($o)
>>   $t = $t.Substring(0,$i) + (N $new) + $t.Substring($i + $o.Length)
>>   [System.IO.File]::WriteAllText((Resolve-Path $path), $t, (New-Object System.Text.UTF8Encoding $false))
>>   Write-Host "patched $path" -ForegroundColor Green
>> }
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> # Hotels.jsx: show stars only if the data has them
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Hotels.jsx" @'
>>                   <span className="flex items-center gap-1 text-sm text-amber-500">
>>                     <FiStar /> {h.stars || (3 + Math.random() * 2).toFixed(1)}
>>                   </span>
>> '@ @'
>>                   {h.stars ? (
>>                     <span className="flex items-center gap-1 text-sm text-amber-500">
>>                       <FiStar /> {h.stars}
>>                     </span>
>>                   ) : null}
>> '@
patched frontend\src\pages\Hotels.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> # Restaurants.jsx: remove the random rating and the unused import
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Restaurants.jsx" @'
>>                   <span className="flex shrink-0 items-center gap-1 text-sm text-amber-500">
>>                     <FiStar /> {(3.8 + Math.random()).toFixed(1)}
>>                   </span>
>>
>> '@ ''
patched frontend\src\pages\Restaurants.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Restaurants.jsx" 'import { FiMapPin, FiStar } from' 'import { FiMapPin } from'
patched frontend\src\pages\Restaurants.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> # Destination.jsx: remove the name-hash "rating"
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Destination.jsx" @'
>>                   <span className="flex items-center gap-1 text-sm text-amber-500">
>>                     <FiStar /> {getStableRating(a.name)}
>>                   </span>
>>
>> '@ ''
patched frontend\src\pages\Destination.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Destination.jsx" 'import { FiStar, FiMapPin, FiSun }' 'import { FiMapPin, FiSun }'
patched frontend\src\pages\Destination.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> $d = N (Get-Content "frontend\src\pages\Destination.jsx" -Raw)
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> $d = [regex]::Replace($d, '// Deterministic "rating".*?\n}\n\n', '', 'Singleline')
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> [System.IO.File]::WriteAllText((Resolve-Path "frontend\src\pages\Destination.jsx"), $d, (New-Object System.Text.UTF8Encoding $false))
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Select-String -Path frontend\src\pages\*.jsx -Pattern "Math.random|getStableRating|FiStar"

frontend\src\pages\Hotels.jsx:1:import { FiStar, FiMapPin, FiDollarSign } from "react-icons/fi";
frontend\src\pages\Hotels.jsx:27:                      <FiStar /> {h.stars}


PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> $readme = @'
>> # DayPlan: Smart Travel Planner
>>
>> Plan a trip, see what is *on the way*, find places beyond the famous ones, and budget it.
>> React (Vite + Tailwind + Leaflet) frontend, Flask + SQLAlchemy + SQLite backend.
>> Live data comes from free, keyless APIs (Nominatim, OSRM, Open-Meteo, Overpass). Curated
>> local CSV datasets back them up, so a slow or dead public server does not empty the page.
>>
>> ## Features
>>
>> | Feature | What it does |
>> |---|---|
>> | Plan a trip | One request (`POST /api/plan-trip`) returns route, weather, attractions, hotels, restaurants, budget and itinerary |
>> | Destination | Tourist attractions near the destination, nearest first (live + curated) |
>> | Highlights | Hidden / authentic spots, with hotels and restaurants filtered out of the list |
>> | **On the Way** | Stops along the driving route (see "Along-the-route stops"), shown as a numbered timeline **and** as numbered markers on the existing Map tab |
>> | Hotels | Live OpenStreetMap hotels. An honest "unavailable" message if the live lookup failed |
>> | Restaurants | Live + curated, with a veg / non-veg / both filter |
>> | Weather, Budget, Itinerary | Open-Meteo forecast, a budget breakdown, a deterministic day-by-day plan |
>> | Accounts | Register / login (JWT), saved trips and favourites |
>>
>> Star ratings are shown only when the data really contains them. Nothing is invented.
>>
>> ## Resilience design
>>
>> Every external call is independent. A failure degrades one section, never the whole request.
>>
>> | Section | Live source | Fallback | If both fail |
>> |---|---|---|---|
>> | Route | OSRM | none | route is `null`, rest of plan still renders |
>> | Weather | Open-Meteo | none | `null` |
>> | Attractions | Overpass | curated tourist spots (459) | empty list |
>> | Restaurants | Overpass | curated restaurants (143 rows) | empty list |
>> | Highlights | Overpass | curated spots | empty list |
>> | Along the route | Overpass (route search) | curated spots near the route | `[]` plus an honest empty state |
>> | Hotels | Overpass | **none yet** (dataset in progress) | `hotelsStatus: "unavailable"` |
>>
>> Rules that apply across the services:
>>
>> - **Blend, don't replace.** If live results number fewer than 5, curated rows are added to them
>>   instead of swapping the whole list.
>> - **Fail-fast cooldown.** After an Overpass outage the app stops calling it for 120 s, so one
>>   dead server does not make every request wait for a timeout.
>> - **Silent failures are treated as failures.** Overpass can answer HTTP 200 with an empty list and
>>   a `runtime error` remark when it is overloaded. That is raised as an error, not read as
>>   "no results".
>> - Route searches never start the global cooldown (`trip_cooldown=False`).
>> - Failures are logged server-side with Python `logging`.
>>
>> ## Along-the-route stops
>>
>> Implemented in `services/corridor_service.py` and `utils/geo.py`.
>>
>> 1. The OSRM route is loaded into a `RouteIndex`. It projects points onto a local flat map and
>>    computes, for any spot, its distance off the route and its distance along the route (km).
>> 2. Candidates are all curated spots plus live OpenStreetMap places. Only spots within
>>    **5 km** of the route are kept. The first and last **10 km** are skipped, because those are
>>    the origin and destination themselves.
>> 3. Hotels and restaurants are excluded (`EXCLUDED_TAGS`).
>> 4. Live and curated duplicates are merged (same normalised name, or under 0.25 km apart).
>> 5. The route is cut into 15 equal stretches, with at most 2 stops per stretch. This stops one
>>    city from supplying all the stops. Curated spots come first within a stretch. Results are
>>    ordered by distance along the route.
>> 6. Live route query: the route is thinned to one waypoint about every 4 km, sent in pieces of 50
>>    points, with at most 6 queries and a 30 s time budget. If the first query fails, the error is
>>    raised. If a later one fails, the partial result is kept.
>>
>> ## Project structure
>> clear
>>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Write-File "$repo\backend\scripts\check_route_query.py" @'
>> """Check the along-the-route Overpass query on its own, with long timeouts.
>>
>> Run from the backend folder:
>>     python scripts/check_route_query.py route.json
>>
>> route.json = the "route" object from /api/plan-trip. For each Overpass server
>> this (1) sends a tiny query, then (2) if that worked, sends the first ~200 km
>> piece of your route, exactly as the app would, and reports time and results.
>> It shows whether the SERVER is the problem or the QUERY is.
>> """
>> import json
>> import os
>> import sys
>> import time
>>
>> sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
>>
>> import requests
>> from config import Config
>> from services import overpass_service
>>
>> TINY = '[out:json][timeout:15];node["tourism"="hotel"](around:3000,19.076,72.8777);out count;'
>> ENDPOINTS = [
>>     ("app default", Config.OVERPASS_URL),
>>     ("kumi mirror", "https://overpass.kumi.systems/api/interpreter"),
>>     ("private.coffee mirror", "https://overpass.private.coffee/api/interpreter"),
>> ]
>>
>>
>> def post(url, query, timeout):
>>     start = time.time()
>>     try:
>>         r = requests.post(url, data={"data": query},
>>                           headers={"User-Agent": Config.USER_AGENT}, timeout=timeout)
>>         return r, round(time.time() - start, 1), None
>>     except requests.RequestException as e:
>>         return None, round(time.time() - start, 1), f"{type(e).__name__}: {str(e)[:120]}"
>>
>>
>> def main(path):
>>     with open(path, encoding="utf-8-sig") as f:
>>         coords = json.load(f)["geometry"]["coordinates"]
>>     waypoints = overpass_service._route_waypoints(coords, overpass_service.ROUTE_STEP_KM)
>>     piece = waypoints[:overpass_service.ROUTE_POINTS_PER_QUERY]
>>     query = overpass_service._route_query(piece, 5000)
>>     print(f"Route has {len(waypoints)} waypoints; first piece = {len(piece)} points\n")
>>
>>     for label, url in ENDPOINTS:
>>         r, took, err = post(url, TINY, 30)
>>         if err or not r.ok:
>>             print(f"{label:24} tiny query FAILED ({took}s) {err or 'HTTP ' + str(r.status_code)}")
>>             continue
>>         print(f"{label:24} tiny query OK ({took}s)")
>>         r, took, err = post(url, query, 90)
>>         if err:
>>             print(f"{'':24} route piece FAILED after {took}s: {err}")
>>         elif not r.ok:
>>             print(f"{'':24} route piece HTTP {r.status_code} after {took}s: {r.text[:200]!r}")
>>         else:
>>             data = r.json()
>>             elements = data.get("elements", [])
>>             names = [e.get("tags", {}).get("name") for e in elements][:8]
>>             print(f"{'':24} route piece HTTP 200 in {took}s: {len(elements)} places, e.g. {names}")
>>             if data.get("remark"):
>>                 print(f"{'':24} !! Overpass remark: {data['remark']}")
>>
>>
>> if __name__ == "__main__":
>>     if len(sys.argv) != 2:
>>         sys.exit("Usage: python scripts/check_route_query.py route.json")
>>     main(sys.argv[1])
>> '@
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> if ($t.Contains("class OverpassRuntimeError")) {
>>   "overpass_service.py already patched"
>> } else {
>>   # Edit 1: the new error type, placed just before _is_outage
>>   $old1 = "def _is_outage(exc):"
>>   $new1 = N @'
>> class OverpassRuntimeError(requests.RequestException):
>>     """Overpass accepted the query but gave up on it (out of time or memory).
>>     It reports this as HTTP 200 with an empty list and a "remark", which would
>>     otherwise look exactly like "there is nothing here"."""
>>
>>
>> def _is_outage(exc):
>> '@
>>
>>   # Edit 2: check the remark after a successful HTTP answer
>>   $old2 = N @'
>>         resp.raise_for_status()
>>         return resp.json()
>>     except requests.RequestException as e:
>>         # Log the REAL reason; the error raised below is deliberately generic.
>>         status = getattr(getattr(e, "response", None), "status_code", None)
>>         reason = f"HTTP {status}" if status else type(e).__name__
>> '@
>>   $new2 = N @'
>>         resp.raise_for_status()
>>         data = resp.json()
>>         remark = data.get("remark", "") if isinstance(data, dict) else ""
>>         if "runtime error" in remark:
>>             raise OverpassRuntimeError(remark)
>>         return data
>>     except requests.RequestException as e:
>>         # Log the REAL reason; the error raised below is deliberately generic.
>>         status = getattr(getattr(e, "response", None), "status_code", None)
>>         reason = f"HTTP {status}" if status else type(e).__name__
>>         if isinstance(e, OverpassRuntimeError):
>>             reason = f"Overpass gave up: {str(e)[:100]}"
>> '@
>>
>>   if (-not $t.Contains($old1)) { throw "Edit 1: '_is_outage' line not found" }
>>   if (-not $t.Contains($old2)) { throw "Edit 2: _query_overpass block not found - send me the file" }
>>   $t = $t.Replace($old1, $new1).Replace($old2, $new2)
>>   Write-File $f $t
>>   "overpass_service.py patched"
>> }
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Write-File "$repo\backend\scripts\check_route_query.py" @'
>> """Check the along-the-route Overpass query on its own, with long timeouts.
>>
>> Run from the backend folder:
>>     python scripts/check_route_query.py route.json
>>
>> route.json = the "route" object from /api/plan-trip. For each Overpass server
>> this (1) sends a tiny query, then (2) if that worked, sends the first ~200 km
>> piece of your route, exactly as the app would, and reports time and results.
>> It shows whether the SERVER is the problem or the QUERY is.
>> """
>> import json
>> import os
>> import sys
>> import time
>>
>> sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
>>
>> import requests
>> from config import Config
>> from services import overpass_service
>>
>> TINY = '[out:json][timeout:15];node["tourism"="hotel"](around:3000,19.076,72.8777);out count;'
>> ENDPOINTS = [
>>     ("app default", Config.OVERPASS_URL),
>>     ("kumi mirror", "https://overpass.kumi.systems/api/interpreter"),
>>     ("private.coffee mirror", "https://overpass.private.coffee/api/interpreter"),
>> ]
>>
>>
>> def post(url, query, timeout):
>>     start = time.time()
>>     try:
>>         r = requests.post(url, data={"data": query},
>>                           headers={"User-Agent": Config.USER_AGENT}, timeout=timeout)
>>         return r, round(time.time() - start, 1), None
>>     except requests.RequestException as e:
>>         return None, round(time.time() - start, 1), f"{type(e).__name__}: {str(e)[:120]}"
>>
>>
>> def main(path):
>>     with open(path, encoding="utf-8-sig") as f:
>>         coords = json.load(f)["geometry"]["coordinates"]
>>     waypoints = overpass_service._route_waypoints(coords, overpass_service.ROUTE_STEP_KM)
>>     piece = waypoints[:overpass_service.ROUTE_POINTS_PER_QUERY]
>>     query = overpass_service._route_query(piece, 5000)
>>     print(f"Route has {len(waypoints)} waypoints; first piece = {len(piece)} points\n")
>>
>>     for label, url in ENDPOINTS:
>>         r, took, err = post(url, TINY, 30)
>>         if err or not r.ok:
>>             print(f"{label:24} tiny query FAILED ({took}s) {err or 'HTTP ' + str(r.status_code)}")
>>             continue
>>         print(f"{label:24} tiny query OK ({took}s)")
>>         r, took, err = post(url, query, 90)
>>         if err:
>>             print(f"{'':24} route piece FAILED after {took}s: {err}")
>>         elif not r.ok:
>>             print(f"{'':24} route piece HTTP {r.status_code} after {took}s: {r.text[:200]!r}")
>>         else:
>>             elements = r.json().get("elements", [])
>>             names = [e.get("tags", {}).get("name") for e in elements][:8]
>>             print(f"{'':24} route piece OK in {took}s: {len(elements)} places, e.g. {names}")
>>
>>
>> if __name__ == "__main__":
>>     if len(sys.argv) != 2:
>>         sys.exit("Usage: python scripts/check_route_query.py route.json")
>>     main(sys.argv[1])
>> '@
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> function N($s){ $s.Replace("`r`n","`n") }
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> function Patch($path, $old, $new){
>>   $t = N (Get-Content $path -Raw)
>>   $o = N $old
>>   if (-not $t.Contains($o)) { Write-Host "NOT FOUND in $path" -ForegroundColor Red; return }
>>   $i = $t.IndexOf($o)
>>   $t = $t.Substring(0,$i) + (N $new) + $t.Substring($i + $o.Length)
>>   [System.IO.File]::WriteAllText((Resolve-Path $path), $t, (New-Object System.Text.UTF8Encoding $false))
>>   Write-Host "patched $path" -ForegroundColor Green
>> }
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> # Hotels.jsx: show stars only if the data has them
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Hotels.jsx" @'
>>                   <span className="flex items-center gap-1 text-sm text-amber-500">
>>                     <FiStar /> {h.stars || (3 + Math.random() * 2).toFixed(1)}
>>                   </span>
>> '@ @'
>>                   {h.stars ? (
>>                     <span className="flex items-center gap-1 text-sm text-amber-500">
>>                       <FiStar /> {h.stars}
>>                     </span>
>>                   ) : null}
>> '@
NOT FOUND in frontend\src\pages\Hotels.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> # Restaurants.jsx: remove the random rating and the unused import
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Restaurants.jsx" @'
>>                   <span className="flex shrink-0 items-center gap-1 text-sm text-amber-500">
>>                     <FiStar /> {(3.8 + Math.random()).toFixed(1)}
>>                   </span>
>>
>> '@ ''
NOT FOUND in frontend\src\pages\Restaurants.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Restaurants.jsx" 'import { FiMapPin, FiStar } from' 'import { FiMapPin } from'
NOT FOUND in frontend\src\pages\Restaurants.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> # Destination.jsx: remove the name-hash "rating"
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Destination.jsx" @'
>>                   <span className="flex items-center gap-1 text-sm text-amber-500">
>>                     <FiStar /> {getStableRating(a.name)}
>>                   </span>
>>
>> '@ ''
NOT FOUND in frontend\src\pages\Destination.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Patch "frontend\src\pages\Destination.jsx" 'import { FiStar, FiMapPin, FiSun }' 'import { FiMapPin, FiSun }'
NOT FOUND in frontend\src\pages\Destination.jsx
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> $d = N (Get-Content "frontend\src\pages\Destination.jsx" -Raw)
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> $d = [regex]::Replace($d, '// Deterministic "rating".*?\n}\n\n', '', 'Singleline')
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> [System.IO.File]::WriteAllText((Resolve-Path "frontend\src\pages\Destination.jsx"), $d, (New-Object System.Text.UTF8Encoding $false))
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan>
PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> Select-String -Path frontend\src\pages\*.jsx -Pattern "Math.random|getStableRating|FiStar"

frontend\src\pages\Hotels.jsx:1:import { FiStar, FiMapPin, FiDollarSign } from "react-icons/fi";
frontend\src\pages\Hotels.jsx:27:                      <FiStar /> {h.stars}


PS C:\Users\samud\OneDrive\Desktop\dayplan\dayplan> $readme = @'
>> # DayPlan: Smart Travel Planner
>>
>> Plan a trip, see what is *on the way*, find places beyond the famous ones, and budget it.
>> React (Vite + Tailwind + Leaflet) frontend, Flask + SQLAlchemy + SQLite backend.
>> Live data comes from free, keyless APIs (Nominatim, OSRM, Open-Meteo, Overpass). Curated
>> local CSV datasets back them up, so a slow or dead public server does not empty the page.
>>
>> ## Features
>>
>> | Feature | What it does |
>> |---|---|
>> | Plan a trip | One request (`POST /api/plan-trip`) returns route, weather, attractions, hotels, restaurants, budget and itinerary |
>> | Destination | Tourist attractions near the destination, nearest first (live + curated) |
>> | Highlights | Hidden / authentic spots, with hotels and restaurants filtered out of the list |
>> | **On the Way** | Stops along the driving route (see "Along-the-route stops"), shown as a numbered timeline **and** as numbered markers on the existing Map tab |
>> | Hotels | Live OpenStreetMap hotels. An honest "unavailable" message if the live lookup failed |
>> | Restaurants | Live + curated, with a veg / non-veg / both filter |
>> | Weather, Budget, Itinerary | Open-Meteo forecast, a budget breakdown, a deterministic day-by-day plan |
>> | Accounts | Register / login (JWT), saved trips and favourites |
>>
>> Star ratings are shown only when the data really contains them. Nothing is invented.
>>
>> ## Resilience design
>>
>> Every external call is independent. A failure degrades one section, never the whole request.
>>
>> | Section | Live source | Fallback | If both fail |
>> |---|---|---|---|
>> | Route | OSRM | none | route is `null`, rest of plan still renders |
>> | Weather | Open-Meteo | none | `null` |
>> | Attractions | Overpass | curated tourist spots (459) | empty list |
>> | Restaurants | Overpass | curated restaurants (143 rows) | empty list |
>> | Highlights | Overpass | curated spots | empty list |
>> | Along the route | Overpass (route search) | curated spots near the route | `[]` plus an honest empty state |
>> | Hotels | Overpass | **none yet** (dataset in progress) | `hotelsStatus: "unavailable"` |
>>
>> Rules that apply across the services:
>>
>> - **Blend, don't replace.** If live results number fewer than 5, curated rows are added to them
>>   instead of swapping the whole list.
>> - **Fail-fast cooldown.** After an Overpass outage the app stops calling it for 120 s, so one
>>   dead server does not make every request wait for a timeout.
>> - **Silent failures are treated as failures.** Overpass can answer HTTP 200 with an empty list and
>>   a `runtime error` remark when it is overloaded. That is raised as an error, not read as
>>   "no results".
>> - Route searches never start the global cooldown (`trip_cooldown=False`).
>> - Failures are logged server-side with Python `logging`.
>>
>> ## Along-the-route stops
>>
>> Implemented in `services/corridor_service.py` and `utils/geo.py`.
>>
>> 1. The OSRM route is loaded into a `RouteIndex`. It projects points onto a local flat map and
>>    computes, for any spot, its distance off the route and its distance along the route (km).
>> 2. Candidates are all curated spots plus live OpenStreetMap places. Only spots within
>>    **5 km** of the route are kept. The first and last **10 km** are skipped, because those are
>>    the origin and destination themselves.
>> 3. Hotels and restaurants are excluded (`EXCLUDED_TAGS`).
>> 4. Live and curated duplicates are merged (same normalised name, or under 0.25 km apart).
>> 5. The route is cut into 15 equal stretches, with at most 2 stops per stretch. This stops one
>>    city from supplying all the stops. Curated spots come first within a stretch. Results are
>>    ordered by distance along the route.
>> 6. Live route query: the route is thinned to one waypoint about every 4 km, sent in pieces of 50
>>    points, with at most 6 queries and a 30 s time budget. If the first query fails, the error is
>>    raised. If a later one fails, the partial result is kept.
>>
>> ## P

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

For `check_corridor.py`, save a route first with
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
- Live attractions may include `amenity=bar` results in Highlights (under review).

## Deployment

- **Frontend (Vercel):** set `VITE_API_URL` to the backend URL, build `npm run build`, output `dist`.
- **Backend (Render):** set `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS`. Start command: `gunicorn app:app`.