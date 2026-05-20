import httpx
import time
from typing import Any

BASE = "https://api.jolpi.ca/ergast/f1"
_cache: dict[str, tuple[Any, float]] = {}


async def _get(path: str, ttl: int = 3600) -> Any:
    if path in _cache:
        data, ts = _cache[path]
        if time.time() - ts < ttl:
            return data
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE}{path}.json?limit=100")
        r.raise_for_status()
        data = r.json()
    _cache[path] = (data, time.time())
    return data


async def get_schedule(year: int):
    data = await _get(f"/{year}", ttl=3600)
    return data.get("MRData", {}).get("RaceTable", {}).get("Races", [])


async def get_race_result(year: int, round_num: int):
    data = await _get(f"/{year}/{round_num}/results", ttl=300)
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return races[0] if races else None


async def get_all_results(year: int):
    data = await _get(f"/{year}/results", ttl=600)
    return data.get("MRData", {}).get("RaceTable", {}).get("Races", [])


async def get_driver_standings(year: int):
    data = await _get(f"/{year}/driverStandings", ttl=600)
    lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    return lists[0].get("DriverStandings", []) if lists else []


async def get_constructor_standings(year: int):
    data = await _get(f"/{year}/constructorStandings", ttl=600)
    lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    return lists[0].get("ConstructorStandings", []) if lists else []


async def get_season_drivers(year: int):
    data = await _get(f"/{year}/drivers", ttl=3600)
    return data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])


async def get_constructor_drivers(year: int, constructor_id: str):
    data = await _get(f"/{year}/constructors/{constructor_id}/drivers", ttl=3600)
    return data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])


async def get_driver_history(driver_id: str):
    data = await _get(f"/drivers/{driver_id}/results", ttl=3600)
    return data.get("MRData", {}).get("RaceTable", {}).get("Races", [])


async def get_driver_seasons(driver_id: str):
    data = await _get(f"/drivers/{driver_id}/seasons", ttl=3600)
    return data.get("MRData", {}).get("SeasonTable", {}).get("Seasons", [])


async def get_constructor_seasons(constructor_id: str):
    data = await _get(f"/constructors/{constructor_id}/seasons", ttl=3600)
    return data.get("MRData", {}).get("SeasonTable", {}).get("Seasons", [])


async def get_qualifying_result(year: int, round_num: int):
    data = await _get(f"/{year}/{round_num}/qualifying", ttl=300)
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return races[0] if races else None


async def get_lap_times(year: int, round_num: int, driver_id: str):
    data = await _get(f"/{year}/{round_num}/drivers/{driver_id}/laps", ttl=3600)
    return data.get("MRData", {}).get("RaceTable", {}).get("Races", [])


async def get_pit_stops(year: int, round_num: int):
    data = await _get(f"/{year}/{round_num}/pitstops", ttl=3600)
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return races[0].get("PitStops", []) if races else []


async def get_fastest_laps(year: int, round_num: int):
    data = await _get(f"/{year}/{round_num}/fastest/1/results", ttl=3600)
    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    return races[0] if races else None


async def get_driver_h2h(year: int, driver1: str, driver2: str):
    d1_results = []
    d2_results = []
    races = await get_all_results(year)
    for race in races:
        results = race.get("Results", [])
        d1 = next((r for r in results if r["Driver"]["driverId"] == driver1), None)
        d2 = next((r for r in results if r["Driver"]["driverId"] == driver2), None)
        if d1 and d2:
            d1_results.append({**d1, "raceName": race["raceName"], "round": race["round"]})
            d2_results.append({**d2, "raceName": race["raceName"], "round": race["round"]})
    return {"driver1": d1_results, "driver2": d2_results}


async def get_constructors(year: int):
    data = await _get(f"/{year}/constructors", ttl=3600)
    return data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])


async def get_driver_career_standings(driver_id: str):
    path = f"/drivers/{driver_id}/driverStandings"
    if path in _cache:
        data, ts = _cache[path]
        if time.time() - ts < 3600:
            return data
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{BASE}{path}.json?limit=100")
        r.raise_for_status()
        raw = r.json()
    lists = raw.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
    _cache[path] = (lists, time.time())
    return lists


async def count_driver_results_at_position(driver_id: str, position: int) -> int:
    path = f"/drivers/{driver_id}/results/{position}"
    cache_key = f"{path}_total"
    if cache_key in _cache:
        data, ts = _cache[cache_key]
        if time.time() - ts < 3600:
            return data
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE}{path}.json?limit=1")
        r.raise_for_status()
        raw = r.json()
    total = int(raw.get("MRData", {}).get("total", 0))
    _cache[cache_key] = (total, time.time())
    return total
