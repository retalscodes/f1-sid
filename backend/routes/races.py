from fastapi import APIRouter
from datetime import datetime, timezone
from services import openf1, jolpica
from services.weather import get_circuit_weather, CIRCUITS

router = APIRouter()

COUNTRY_TO_CIRCUIT_KEY = {
    "Bahrain": "bahrain", "Saudi Arabia": "saudi_arabia", "Australia": "australia",
    "Japan": "japan", "China": "china", "United States": "miami",
    "Italy": "emilia_romagna", "Monaco": "monaco", "Canada": "canada",
    "Spain": "spain", "Austria": "austria", "Great Britain": "britain",
    "Belgium": "belgium", "Hungary": "hungary", "Netherlands": "netherlands",
    "Singapore": "singapore", "Mexico": "mexico", "Brazil": "brazil",
    "Qatar": "qatar", "Abu Dhabi": "abu_dhabi", "Azerbaijan": "azerbaijan",
}


@router.get("/schedule")
async def get_schedule(year: int = None):
    if year is None:
        year = datetime.now().year
    return await jolpica.get_schedule(year)


@router.get("/next")
async def get_next_race():
    year = datetime.now().year
    schedule = await jolpica.get_schedule(year)
    now = datetime.now(timezone.utc).isoformat()
    future = [r for r in schedule if r.get("date", "") >= now[:10]]
    if not future:
        return {"message": "Season complete"}
    next_race = future[0]
    circuit_key = COUNTRY_TO_CIRCUIT_KEY.get(next_race.get("Circuit", {}).get("Location", {}).get("country", ""), "")
    weather = {}
    if circuit_key:
        try:
            weather = await get_circuit_weather(circuit_key)
        except Exception:
            pass
    return {**next_race, "weather": weather, "circuit_key": circuit_key}


@router.get("/countdown")
async def get_countdown():
    year = datetime.now().year
    schedule = await jolpica.get_schedule(year)
    now = datetime.now(timezone.utc)
    for race in schedule:
        race_date = race.get("date", "")
        race_time = race.get("time", "00:00:00Z").replace("Z", "+00:00")
        try:
            race_dt = datetime.fromisoformat(f"{race_date}T{race_time}")
            if race_dt > now:
                delta = race_dt - now
                return {
                    "race_name": race.get("raceName"),
                    "circuit": race.get("Circuit", {}).get("circuitName"),
                    "country": race.get("Circuit", {}).get("Location", {}).get("country"),
                    "race_datetime": race_dt.isoformat(),
                    "days": delta.days,
                    "hours": delta.seconds // 3600,
                    "minutes": (delta.seconds % 3600) // 60,
                    "seconds": delta.seconds % 60,
                    "total_seconds": int(delta.total_seconds()),
                    "round": race.get("round"),
                    "sessions": {
                        "fp1": race.get("FirstPractice"),
                        "fp2": race.get("SecondPractice"),
                        "fp3": race.get("ThirdPractice"),
                        "qualifying": race.get("Qualifying"),
                        "sprint": race.get("Sprint"),
                    },
                }
        except Exception:
            continue
    return {"message": "No upcoming races"}


@router.get("/weekend/{year}/{round}")
async def get_race_weekend(year: int, round: int):
    result = await jolpica.get_race_result(year, round)
    quali = await jolpica.get_qualifying_result(year, round)
    pit_stops = await jolpica.get_pit_stops(year, round)
    fastest = await jolpica.get_fastest_laps(year, round)
    return {
        "result": result,
        "qualifying": quali,
        "pit_stops": pit_stops,
        "fastest_lap": fastest,
    }


@router.get("/weather/{circuit_key}")
async def circuit_weather(circuit_key: str):
    return await get_circuit_weather(circuit_key)
