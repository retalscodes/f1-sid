from fastapi import APIRouter
from datetime import datetime
from services import jolpica

router = APIRouter()

CONSTRUCTOR_INFO = {
    "red_bull":    {"name": "Red Bull Racing",  "color": "#3671C6", "flag": "🇦🇹"},
    "ferrari":     {"name": "Scuderia Ferrari", "color": "#E8002D", "flag": "🇮🇹"},
    "mercedes":    {"name": "Mercedes",         "color": "#27F4D2", "flag": "🇩🇪"},
    "mclaren":     {"name": "McLaren",          "color": "#FF8000", "flag": "🇬🇧"},
    "aston_martin":{"name": "Aston Martin",     "color": "#229971", "flag": "🇬🇧"},
    "alpine":      {"name": "Alpine F1 Team",   "color": "#0093CC", "flag": "🇫🇷"},
    "williams":    {"name": "Williams",         "color": "#64C4FF", "flag": "🇬🇧"},
    "haas":        {"name": "Haas F1 Team",     "color": "#B6BABD", "flag": "🇺🇸"},
    "rb":          {"name": "RB F1 Team",       "color": "#6692FF", "flag": "🇮🇹"},
    "kick_sauber": {"name": "Kick Sauber",      "color": "#52E252", "flag": "🇨🇭"},
}


@router.get("/seasons")
async def list_seasons():
    current = datetime.now().year
    return list(range(current, 1949, -1))


@router.get("/constructors")
async def list_constructors():
    return CONSTRUCTOR_INFO


@router.get("/constructor/{constructor_id}")
async def constructor_history(constructor_id: str):
    seasons = await jolpica.get_constructor_seasons(constructor_id)
    info = CONSTRUCTOR_INFO.get(constructor_id, {})
    return {"constructor_id": constructor_id, "info": info, "seasons": seasons}


@router.get("/constructor/{constructor_id}/{year}/drivers")
async def constructor_season_drivers(constructor_id: str, year: int):
    drivers = await jolpica.get_constructor_drivers(year, constructor_id)
    standings = await jolpica.get_driver_standings(year)
    standings_map = {s["Driver"]["driverId"]: s for s in standings}
    enriched = []
    for d in drivers:
        did = d.get("driverId", "")
        standing = standings_map.get(did, {})
        enriched.append({
            **d,
            "points": standing.get("points", "—"),
            "wins": standing.get("wins", "—"),
            "position": standing.get("position", "—"),
        })
    return enriched


@router.get("/driver/{driver_id}")
async def driver_profile(driver_id: str):
    seasons = await jolpica.get_driver_seasons(driver_id)
    return {"driver_id": driver_id, "seasons": seasons}


@router.get("/driver/{driver_id}/results/{year}")
async def driver_year_results(driver_id: str, year: int):
    races = await jolpica.get_all_results(year)
    results = []
    for race in races:
        for r in race.get("Results", []):
            if r["Driver"]["driverId"] == driver_id:
                results.append({
                    "round": race["round"],
                    "raceName": race["raceName"],
                    "circuit": race["Circuit"]["circuitName"],
                    "country": race["Circuit"]["Location"]["country"],
                    "date": race["date"],
                    "position": r.get("position"),
                    "points": r.get("points"),
                    "grid": r.get("grid"),
                    "status": r.get("status"),
                    "fastest_lap": r.get("FastestLap", {}).get("rank") == "1",
                    "time": r.get("Time", {}).get("time", ""),
                })
    return results


@router.get("/season/{year}")
async def season_overview(year: int):
    driver_standings = await jolpica.get_driver_standings(year)
    constructor_standings = await jolpica.get_constructor_standings(year)
    schedule = await jolpica.get_schedule(year)
    return {
        "year": year,
        "driver_standings": driver_standings,
        "constructor_standings": constructor_standings,
        "races": len(schedule),
        "schedule": schedule,
    }


@router.get("/h2h/{year}/{driver1}/{driver2}")
async def head_to_head(year: int, driver1: str, driver2: str):
    data = await jolpica.get_driver_h2h(year, driver1, driver2)
    d1_wins = sum(1 for a, b in zip(data["driver1"], data["driver2"])
                  if int(a.get("position", 99)) < int(b.get("position", 99)))
    d2_wins = sum(1 for a, b in zip(data["driver1"], data["driver2"])
                  if int(b.get("position", 99)) < int(a.get("position", 99)))
    d1_pts = sum(float(r.get("points", 0)) for r in data["driver1"])
    d2_pts = sum(float(r.get("points", 0)) for r in data["driver2"])
    d1_podiums = sum(1 for r in data["driver1"] if int(r.get("position", 99)) <= 3)
    d2_podiums = sum(1 for r in data["driver2"] if int(r.get("position", 99)) <= 3)
    d1_wins_count = sum(1 for r in data["driver1"] if r.get("position") == "1")
    d2_wins_count = sum(1 for r in data["driver2"] if r.get("position") == "1")
    return {
        "year": year,
        "races": data,
        "summary": {
            "driver1": {"id": driver1, "h2h_wins": d1_wins, "points": d1_pts, "podiums": d1_podiums, "race_wins": d1_wins_count},
            "driver2": {"id": driver2, "h2h_wins": d2_wins, "points": d2_pts, "podiums": d2_podiums, "race_wins": d2_wins_count},
        },
    }


@router.get("/season/{year}/drivers")
async def season_drivers(year: int):
    return await jolpica.get_season_drivers(year)


@router.get("/career/{driver_id}")
async def career_stats(driver_id: str):
    standings_lists = await jolpica.get_driver_career_standings(driver_id)
    if not standings_lists:
        return {"error": f"No data found for driver '{driver_id}'"}

    total_wins = 0
    total_points = 0.0
    championships = 0
    best_position = 99
    seasons_data = []

    for sl in standings_lists:
        year = sl.get("season")
        standings = sl.get("DriverStandings", [])
        if standings:
            s = standings[0]
            wins = int(s.get("wins", 0))
            pts = float(s.get("points", 0))
            pos = int(s.get("position", 99))
            total_wins += wins
            total_points += pts
            if pos == 1:
                championships += 1
            if pos < best_position:
                best_position = pos
            seasons_data.append({"year": year, "position": pos, "wins": wins, "points": pts})

    p2_count = await jolpica.count_driver_results_at_position(driver_id, 2)
    p3_count = await jolpica.count_driver_results_at_position(driver_id, 3)
    podiums = total_wins + p2_count + p3_count

    driver_info = {}
    for sl in standings_lists:
        first_standings = sl.get("DriverStandings", [])
        if first_standings:
            d = first_standings[0].get("Driver", {})
            if d:
                driver_info = {
                    "givenName": d.get("givenName", ""),
                    "familyName": d.get("familyName", driver_id),
                    "nationality": d.get("nationality", ""),
                    "dateOfBirth": d.get("dateOfBirth", ""),
                    "driverId": d.get("driverId", driver_id),
                }
                break

    seasons_sorted = sorted(seasons_data, key=lambda x: x["year"])
    first_season = seasons_sorted[0]["year"] if seasons_sorted else "—"
    last_season = seasons_sorted[-1]["year"] if seasons_sorted else "—"

    return {
        "driver_id": driver_id,
        "driver": driver_info,
        "championships": championships,
        "wins": total_wins,
        "podiums": podiums,
        "points": round(total_points, 1),
        "seasons_count": len(seasons_data),
        "first_season": first_season,
        "last_season": last_season,
        "best_championship": best_position if seasons_data else 99,
        "seasons": seasons_sorted,
    }
