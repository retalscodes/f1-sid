from fastapi import APIRouter
from services import jolpica
from services.weather import CIRCUITS, get_circuit_weather

router = APIRouter()

CIRCUIT_FACTS = {
    "monaco": {
        "lap_record": "1:12.909 — Lewis Hamilton (2021)",
        "length_km": 3.337,
        "turns": 19,
        "drs_zones": 1,
        "first_gp": 1950,
        "fun_fact": "The swimming pool section is literally next to a swimming pool. Very fancy. Sid approves.",
        "overtaking_difficulty": "Nearly impossible. This is where strategy wins.",
        "sid_quote": "Monaco is like trying to run through my ice cave without knocking anything over. IMPOSSIBLE but beautiful!",
    },
    "spa": {
        "lap_record": "1:41.252 — Valtteri Bottas (2018)",
        "length_km": 7.004,
        "turns": 19,
        "drs_zones": 2,
        "first_gp": 1950,
        "fun_fact": "Eau Rouge / Raidillon is considered one of the most iconic corners in motorsport.",
        "overtaking_difficulty": "Good. Kemmel straight provides great overtaking.",
        "sid_quote": "Spa in the rain is CHAOS. I once slid down a glacier in similar conditions. Did not end well.",
    },
    "silverstone": {
        "lap_record": "1:27.097 — Max Verstappen (2020)",
        "length_km": 5.891,
        "turns": 18,
        "drs_zones": 2,
        "first_gp": 1950,
        "fun_fact": "Copse corner is taken at nearly 300 km/h. Sid would not survive this.",
        "overtaking_difficulty": "Moderate. Vale and Wellington Straight help.",
        "sid_quote": "Copse at full speed?! Even I wouldn't attempt that, and I survived the Ice Age!",
    },
    "monza": {
        "lap_record": "1:21.046 — Rubens Barrichello (2004)",
        "length_km": 5.793,
        "turns": 11,
        "drs_zones": 2,
        "first_gp": 1950,
        "fun_fact": "The Temple of Speed. Highest average speeds on the calendar.",
        "overtaking_difficulty": "Excellent. Multiple opportunities at the chicanes.",
        "sid_quote": "Monza is pure SPEED. Even a sloth would be fast here. Well... maybe not THIS sloth.",
    },
    "suzuka": {
        "lap_record": "1:30.983 — Lewis Hamilton (2019)",
        "length_km": 5.807,
        "turns": 18,
        "drs_zones": 1,
        "first_gp": 1987,
        "fun_fact": "The only figure-8 circuit on the F1 calendar, with a distinctive crossover.",
        "overtaking_difficulty": "Difficult but rewarding. Spoon and 130R are legendary.",
        "sid_quote": "A figure-8 track?! Even my mammoth friends couldn't draw that in the snow. Genius humans!",
    },
}


@router.get("/")
async def list_circuits():
    return [{"key": k, **v} for k, v in CIRCUITS.items()]


@router.get("/{circuit_key}")
async def circuit_dna(circuit_key: str):
    circuit = CIRCUITS.get(circuit_key)
    if not circuit:
        return {"error": "Circuit not found"}
    facts = CIRCUIT_FACTS.get(circuit_key, {})
    weather = {}
    try:
        weather = await get_circuit_weather(circuit_key)
    except Exception:
        pass
    winners = await get_circuit_winners(circuit_key)
    return {
        "key": circuit_key,
        **circuit,
        **facts,
        "weather": weather,
        "past_winners": winners[:10],
    }


async def get_circuit_winners(circuit_key: str) -> list:
    circuit_id_map = {
        "monaco": "monaco", "britain": "silverstone", "italy": "monza",
        "japan": "suzuka", "bahrain": "bahrain", "spain": "catalunya",
        "belgium": "spa", "hungary": "hungaroring", "austria": "red_bull_ring",
        "netherlands": "zandvoort", "singapore": "marina_bay",
        "australia": "albert_park", "canada": "villeneuve",
        "usa": "americas", "mexico": "rodriguez", "brazil": "interlagos",
        "azerbaijan": "baku", "abu_dhabi": "yas_marina",
    }
    ergast_id = circuit_id_map.get(circuit_key)
    if not ergast_id:
        return []
    try:
        import httpx, time
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://api.jolpi.ca/ergast/f1/circuits/{ergast_id}/results/1.json?limit=30")
            data = r.json()
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return [
            {
                "year": race["season"],
                "winner": f"{race['Results'][0]['Driver']['givenName']} {race['Results'][0]['Driver']['familyName']}",
                "constructor": race["Results"][0]["Constructor"]["name"],
                "time": race["Results"][0].get("Time", {}).get("time", ""),
            }
            for race in sorted(races, key=lambda x: x["season"], reverse=True)
            if race.get("Results")
        ]
    except Exception:
        return []
