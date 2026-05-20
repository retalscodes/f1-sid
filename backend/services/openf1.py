import httpx
import time
from typing import Any

BASE = "https://api.openf1.org/v1"
_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL = 30  # seconds for live data


async def _get(path: str, params: dict | None = None, ttl: int = CACHE_TTL) -> Any:
    key = path + str(sorted((params or {}).items()))
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < ttl:
            return data
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE}{path}", params=params)
        r.raise_for_status()
        data = r.json()
    _cache[key] = (data, time.time())
    return data


async def get_latest_session():
    sessions = await _get("/sessions", {"session_type": "Race"}, ttl=60)
    if not sessions:
        return None
    return sorted(sessions, key=lambda s: s.get("date_start", ""), reverse=True)[0]


async def get_sessions_for_meeting(meeting_key: int):
    return await _get("/sessions", {"meeting_key": meeting_key}, ttl=300)


async def get_meetings(year: int):
    return await _get("/meetings", {"year": year}, ttl=3600)


async def get_latest_meeting():
    from datetime import datetime, timezone
    meetings = await get_meetings(datetime.now().year)
    if not meetings:
        return None
    now = datetime.now(timezone.utc).isoformat()
    past = [m for m in meetings if m.get("date_start", "") <= now]
    return sorted(past, key=lambda m: m.get("date_start", ""), reverse=True)[0] if past else meetings[0]


async def get_next_meeting():
    from datetime import datetime, timezone
    meetings = await get_meetings(datetime.now().year)
    if not meetings:
        return None
    now = datetime.now(timezone.utc).isoformat()
    future = [m for m in meetings if m.get("date_start", "") > now]
    return sorted(future, key=lambda m: m.get("date_start", ""))[0] if future else None


async def get_drivers(session_key: int):
    return await _get("/drivers", {"session_key": session_key}, ttl=300)


async def get_positions(session_key: int):
    return await _get("/position", {"session_key": session_key}, ttl=15)


async def get_latest_positions(session_key: int):
    data = await get_positions(session_key)
    latest: dict[int, dict] = {}
    for item in data:
        drv = item.get("driver_number")
        if drv not in latest or item.get("date", "") > latest[drv].get("date", ""):
            latest[drv] = item
    return sorted(latest.values(), key=lambda x: x.get("position", 99))


async def get_intervals(session_key: int):
    return await _get("/intervals", {"session_key": session_key}, ttl=15)


async def get_stints(session_key: int):
    return await _get("/stints", {"session_key": session_key}, ttl=30)


async def get_pit_stops(session_key: int):
    return await _get("/pit", {"session_key": session_key}, ttl=30)


async def get_laps(session_key: int, driver_number: int | None = None):
    params: dict = {"session_key": session_key}
    if driver_number:
        params["driver_number"] = driver_number
    return await _get("/laps", params, ttl=30)


async def get_weather(session_key: int):
    return await _get("/weather", {"session_key": session_key}, ttl=60)


async def get_race_control(session_key: int):
    return await _get("/race_control", {"session_key": session_key}, ttl=20)


async def get_team_radio(session_key: int):
    return await _get("/team_radio", {"session_key": session_key}, ttl=60)


async def get_car_data(session_key: int, driver_number: int):
    return await _get("/car_data", {"session_key": session_key, "driver_number": driver_number}, ttl=15)


async def is_session_active(session_key: int) -> bool:
    from datetime import datetime, timezone
    sessions = await _get("/sessions", {"session_key": session_key}, ttl=60)
    if not sessions:
        return False
    s = sessions[0]
    now = datetime.now(timezone.utc).isoformat()
    return bool(s.get("date_start", "") <= now <= s.get("date_end", ""))
