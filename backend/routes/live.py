from fastapi import APIRouter, HTTPException
from services import openf1

router = APIRouter()


@router.get("/status")
async def live_status():
    meeting = await openf1.get_latest_meeting()
    if not meeting:
        return {"active": False, "message": "No session data"}
    sessions = await openf1.get_sessions_for_meeting(meeting["meeting_key"])
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    active = [s for s in sessions if s.get("date_start", "") <= now <= s.get("date_end", "")]
    if active:
        session = active[0]
        return {"active": True, "session": session, "meeting": meeting}
    upcoming = [s for s in sessions if s.get("date_start", "") > now]
    if upcoming:
        next_s = sorted(upcoming, key=lambda x: x["date_start"])[0]
        return {"active": False, "upcoming_session": next_s, "meeting": meeting}
    return {"active": False, "last_meeting": meeting, "message": "Between sessions"}


@router.get("/positions/{session_key}")
async def live_positions(session_key: int):
    positions = await openf1.get_latest_positions(session_key)
    drivers = await openf1.get_drivers(session_key)
    driver_map = {d["driver_number"]: d for d in drivers}
    result = []
    for pos in positions:
        drv_num = pos.get("driver_number")
        driver = driver_map.get(drv_num, {})
        result.append({
            "position": pos.get("position"),
            "driver_number": drv_num,
            "name": f"{driver.get('first_name', '')} {driver.get('last_name', '')}".strip(),
            "short_name": driver.get("name_acronym", ""),
            "team": driver.get("team_name", ""),
            "team_colour": f"#{driver.get('team_colour', 'FFFFFF')}",
            "country_code": driver.get("country_code", ""),
            "headshot_url": driver.get("headshot_url", ""),
        })
    return result


@router.get("/intervals/{session_key}")
async def live_intervals(session_key: int):
    return await openf1.get_intervals(session_key)


@router.get("/stints/{session_key}")
async def live_stints(session_key: int):
    stints = await openf1.get_stints(session_key)
    drivers = await openf1.get_drivers(session_key)
    driver_map = {d["driver_number"]: d for d in drivers}
    enriched = []
    for s in stints:
        drv = driver_map.get(s.get("driver_number"), {})
        enriched.append({
            **s,
            "driver_name": f"{drv.get('first_name', '')} {drv.get('last_name', '')}".strip(),
            "team": drv.get("team_name", ""),
            "team_colour": f"#{drv.get('team_colour', 'FFFFFF')}",
        })
    return enriched


@router.get("/weather/{session_key}")
async def live_weather(session_key: int):
    data = await openf1.get_weather(session_key)
    return data[-1] if data else {}


@router.get("/race-control/{session_key}")
async def live_race_control(session_key: int):
    data = await openf1.get_race_control(session_key)
    return sorted(data, key=lambda x: x.get("date", ""), reverse=True)[:20]


@router.get("/radio/{session_key}")
async def live_radio(session_key: int):
    data = await openf1.get_team_radio(session_key)
    drivers = await openf1.get_drivers(session_key)
    driver_map = {d["driver_number"]: d for d in drivers}
    enriched = []
    for r in sorted(data, key=lambda x: x.get("date", ""), reverse=True)[:30]:
        drv = driver_map.get(r.get("driver_number"), {})
        enriched.append({
            **r,
            "driver_name": f"{drv.get('first_name', '')} {drv.get('last_name', '')}".strip(),
            "team": drv.get("team_name", ""),
            "team_colour": f"#{drv.get('team_colour', 'FFFFFF')}",
        })
    return enriched


@router.get("/pit-stops/{session_key}")
async def live_pit_stops(session_key: int):
    return await openf1.get_pit_stops(session_key)


@router.get("/latest-session")
async def get_latest_session():
    return await openf1.get_latest_session()
