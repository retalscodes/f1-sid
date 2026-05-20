import httpx
import time
from typing import Any

BASE = "https://api.open-meteo.com/v1/forecast"
_cache: dict[str, tuple[Any, float]] = {}

CIRCUITS: dict[str, dict] = {
    "bahrain":       {"name": "Bahrain International Circuit",     "lat": 26.0325,  "lng": 50.5106,   "country": "Bahrain",     "flag": "🇧🇭"},
    "saudi_arabia":  {"name": "Jeddah Corniche Circuit",           "lat": 21.6319,  "lng": 39.1044,   "country": "Saudi Arabia","flag": "🇸🇦"},
    "australia":     {"name": "Albert Park Circuit",               "lat": -37.8497, "lng": 144.9680,  "country": "Australia",   "flag": "🇦🇺"},
    "japan":         {"name": "Suzuka Circuit",                    "lat": 34.8431,  "lng": 136.5415,  "country": "Japan",       "flag": "🇯🇵"},
    "china":         {"name": "Shanghai International Circuit",    "lat": 31.3389,  "lng": 121.2197,  "country": "China",       "flag": "🇨🇳"},
    "miami":         {"name": "Miami International Autodrome",     "lat": 25.9581,  "lng": -80.2389,  "country": "USA",         "flag": "🇺🇸"},
    "emilia_romagna":{"name": "Autodromo Enzo e Dino Ferrari",     "lat": 44.3439,  "lng": 11.7167,   "country": "Italy",       "flag": "🇮🇹"},
    "monaco":        {"name": "Circuit de Monaco",                 "lat": 43.7347,  "lng": 7.4206,    "country": "Monaco",      "flag": "🇲🇨"},
    "canada":        {"name": "Circuit Gilles Villeneuve",         "lat": 45.5000,  "lng": -73.5228,  "country": "Canada",      "flag": "🇨🇦"},
    "spain":         {"name": "Circuit de Barcelona-Catalunya",    "lat": 41.5700,  "lng": 2.2611,    "country": "Spain",       "flag": "🇪🇸"},
    "austria":       {"name": "Red Bull Ring",                     "lat": 47.2197,  "lng": 14.7647,   "country": "Austria",     "flag": "🇦🇹"},
    "britain":       {"name": "Silverstone Circuit",               "lat": 52.0786,  "lng": -1.0169,   "country": "UK",          "flag": "🇬🇧"},
    "belgium":       {"name": "Circuit de Spa-Francorchamps",      "lat": 50.4372,  "lng": 5.9714,    "country": "Belgium",     "flag": "🇧🇪"},
    "hungary":       {"name": "Hungaroring",                       "lat": 47.5789,  "lng": 19.2486,   "country": "Hungary",     "flag": "🇭🇺"},
    "netherlands":   {"name": "Circuit Zandvoort",                 "lat": 52.3888,  "lng": 4.5409,    "country": "Netherlands", "flag": "🇳🇱"},
    "italy":         {"name": "Autodromo Nazionale Monza",         "lat": 45.6156,  "lng": 9.2811,    "country": "Italy",       "flag": "🇮🇹"},
    "azerbaijan":    {"name": "Baku City Circuit",                 "lat": 40.3725,  "lng": 49.8533,   "country": "Azerbaijan",  "flag": "🇦🇿"},
    "singapore":     {"name": "Marina Bay Street Circuit",         "lat": 1.2914,   "lng": 103.8644,  "country": "Singapore",   "flag": "🇸🇬"},
    "usa":           {"name": "Circuit of The Americas",           "lat": 30.1328,  "lng": -97.6411,  "country": "USA",         "flag": "🇺🇸"},
    "mexico":        {"name": "Autódromo Hermanos Rodríguez",      "lat": 19.4042,  "lng": -99.0907,  "country": "Mexico",      "flag": "🇲🇽"},
    "brazil":        {"name": "Autódromo José Carlos Pace",        "lat": -23.7036, "lng": -46.6997,  "country": "Brazil",      "flag": "🇧🇷"},
    "las_vegas":     {"name": "Las Vegas Street Circuit",          "lat": 36.1147,  "lng": -115.1728, "country": "USA",         "flag": "🇺🇸"},
    "qatar":         {"name": "Lusail International Circuit",      "lat": 25.4900,  "lng": 51.4542,   "country": "Qatar",       "flag": "🇶🇦"},
    "abu_dhabi":     {"name": "Yas Marina Circuit",                "lat": 24.4672,  "lng": 54.6031,   "country": "UAE",         "flag": "🇦🇪"},
}


async def get_circuit_weather(circuit_key: str) -> dict:
    circuit = CIRCUITS.get(circuit_key)
    if not circuit:
        return {}
    key = circuit_key
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < 1800:
            return data
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(BASE, params={
            "latitude": circuit["lat"],
            "longitude": circuit["lng"],
            "hourly": "temperature_2m,precipitation_probability,windspeed_10m,weathercode",
            "current_weather": "true",
            "timezone": "auto",
            "forecast_days": 3,
        })
        r.raise_for_status()
        raw = r.json()
    current = raw.get("current_weather", {})
    result = {
        "circuit": circuit["name"],
        "country": circuit["country"],
        "flag": circuit["flag"],
        "temperature": current.get("temperature"),
        "windspeed": current.get("windspeed"),
        "weathercode": current.get("weathercode"),
        "is_day": current.get("is_day"),
        "hourly": {
            "time": raw.get("hourly", {}).get("time", [])[:24],
            "temperature": raw.get("hourly", {}).get("temperature_2m", [])[:24],
            "rain_prob": raw.get("hourly", {}).get("precipitation_probability", [])[:24],
            "wind": raw.get("hourly", {}).get("windspeed_10m", [])[:24],
        },
    }
    _cache[key] = (result, time.time())
    return result
