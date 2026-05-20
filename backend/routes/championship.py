from fastapi import APIRouter
from services import jolpica
from datetime import datetime

router = APIRouter()


@router.get("/drivers")
async def driver_championship(year: int = None):
    year = year or datetime.now().year
    standings = await jolpica.get_driver_standings(year)
    return {"year": year, "standings": standings}


@router.get("/constructors")
async def constructor_championship(year: int = None):
    year = year or datetime.now().year
    standings = await jolpica.get_constructor_standings(year)
    return {"year": year, "standings": standings}


@router.get("/battle")
async def championship_battle(year: int = None):
    year = year or datetime.now().year
    driver_standings = await jolpica.get_driver_standings(year)
    constructor_standings = await jolpica.get_constructor_standings(year)
    top3_drivers = driver_standings[:3]
    top3_constructors = constructor_standings[:3]
    gaps = []
    for i in range(1, min(3, len(top3_drivers))):
        leader_pts = float(top3_drivers[0].get("points", 0))
        competitor_pts = float(top3_drivers[i].get("points", 0))
        gaps.append({
            "driver": top3_drivers[i]["Driver"]["familyName"],
            "gap": leader_pts - competitor_pts,
        })
    return {
        "year": year,
        "leader": top3_drivers[0] if top3_drivers else None,
        "top3_drivers": top3_drivers,
        "top3_constructors": top3_constructors,
        "gaps_to_leader": gaps,
    }


@router.get("/history/{driver_id}")
async def driver_championship_history(driver_id: str):
    seasons = await jolpica.get_driver_seasons(driver_id)
    results = []
    for s in seasons:
        year = int(s.get("season", 0))
        if year < 1990:
            continue
        try:
            standings = await jolpica.get_driver_standings(year)
            standing = next((x for x in standings if x["Driver"]["driverId"] == driver_id), None)
            if standing:
                results.append({"year": year, "position": standing.get("position"), "points": standing.get("points"), "wins": standing.get("wins")})
        except Exception:
            continue
    return results
