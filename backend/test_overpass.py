import requests

query = '[out:json][timeout:15];node["tourism"="hotel"](around:3000,19.0549990,72.8692035);out;'
r = requests.post('https://overpass-api.de/api/interpreter', data={'data': query}, timeout=15)
print(r.status_code)
print(r.text[:300])
