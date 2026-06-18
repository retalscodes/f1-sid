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
    # Build list of IDs to try (handle multi-word like michael_schumacher → schumacher)
    ids_to_try = [driver_id]
    if "_" in driver_id:
        ids_to_try.append(driver_id.split("_")[-1])

    # Find working ID via race win count (most reliable endpoint)
    working_id = None
    wins = 0
    for did in ids_to_try:
        w = await jolpica.count_driver_results_at_position(did, 1)
        if w is not None and (w > 0 or did == driver_id):
            working_id = did
            wins = w
            break

    if working_id is None:
        working_id = driver_id

    # Verify driver exists — total race starts
    total_starts = await jolpica.count_driver_results_at_position(working_id, 1)
    # If wins came back 0, also check if any results exist at all via P2
    p2 = await jolpica.count_driver_results_at_position(working_id, 2)
    p3 = await jolpica.count_driver_results_at_position(working_id, 3)

    # If no data found, try remaining IDs
    if wins == 0 and p2 == 0 and p3 == 0:
        for did in ids_to_try[1:]:
            w2 = await jolpica.count_driver_results_at_position(did, 1)
            p2b = await jolpica.count_driver_results_at_position(did, 2)
            p3b = await jolpica.count_driver_results_at_position(did, 3)
            if w2 > 0 or p2b > 0 or p3b > 0:
                working_id = did
                wins, p2, p3 = w2, p2b, p3b
                break

    if wins == 0 and p2 == 0 and p3 == 0:
        return {"error": f"No data found for driver '{driver_id}'. Check the Ergast driver ID."}

    podiums = wins + p2 + p3

    # Championship seasons (P1 in final standings)
    champ_seasons = await jolpica.get_driver_championship_seasons(working_id)
    championships = len(champ_seasons)

    # All seasons competed
    season_years = await jolpica.get_driver_season_years(working_id)
    seasons_count = len(season_years)
    first_season = season_years[0] if season_years else "—"
    last_season = season_years[-1] if season_years else "—"

    # Driver info (name, nationality)
    driver_info = await jolpica.get_driver_info(working_id)

    # Career points from standings (best effort)
    standings_lists = await jolpica.get_driver_career_standings(working_id)
    total_points = 0.0
    best_position = 99
    seasons_data = []
    for sl in standings_lists:
        yr = sl.get("season")
        standing = sl.get("DriverStandings", [])
        if standing:
            s = standing[0]
            pts = float(s.get("points", 0))
            pos = int(s.get("position", 99))
            w = int(s.get("wins", 0))
            total_points += pts
            if pos < best_position:
                best_position = pos
            seasons_data.append({"year": yr, "position": pos, "wins": w, "points": pts})

    return {
        "driver_id": working_id,
        "driver": driver_info,
        "championships": championships,
        "wins": wins,
        "podiums": podiums,
        "points": round(total_points, 1),
        "seasons_count": seasons_count,
        "first_season": first_season,
        "last_season": last_season,
        "best_championship": best_position if seasons_data else (1 if championships > 0 else 99),
        "seasons": sorted(seasons_data, key=lambda x: x["year"]),
    }
