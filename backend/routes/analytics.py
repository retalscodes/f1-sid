from fastapi import APIRouter, Query
from services import jolpica
from services import fastf1_service
import json, time

router = APIRouter()


@router.get("/rounds/{year}")
async def available_rounds(year: int):
    return await fastf1_service.get_available_rounds(year)


@router.get("/lap-comparison/{year}/{round_num}")
async def lap_comparison(
    year: int,
    round_num: int,
    d1: str = Query(..., description="Driver 3-letter abbreviation e.g. VER"),
    d2: str = Query(..., description="Driver 3-letter abbreviation e.g. HAM"),
):
    data = await fastf1_service.get_lap_comparison(year, round_num, d1.upper(), d2.upper())
    return data


@router.get("/tire-strategy/{year}/{round_num}")
async def tire_strategy(year: int, round_num: int):
    return await fastf1_service.get_tire_strategy(year, round_num)


@router.get("/quali-comparison/{year}/{round_num}")
async def quali_comparison(
    year: int,
    round_num: int,
    d1: str = Query(...),
    d2: str = Query(...),
):
    return await fastf1_service.get_quali_comparison(year, round_num, d1.upper(), d2.upper())


@router.get("/season-duel/{year}/{driver1}/{driver2}")
async def season_duel_analytics(year: int, driver1: str, driver2: str):
    """Full season analysis for two drivers with points progression."""
    races = await jolpica.get_all_results(year)
    standings = await jolpica.get_driver_standings(year)

    d1_pts_prog, d2_pts_prog = [], []
    d1_total, d2_total = 0.0, 0.0
    race_labels, positions = [], []

    for race in races:
        results = race.get("Results", [])
        d1 = next((r for r in results if r["Driver"]["driverId"] == driver1), None)
        d2 = next((r for r in results if r["Driver"]["driverId"] == driver2), None)
        if not d1 or not d2:
            continue
        d1_total += float(d1.get("points", 0))
        d2_total += float(d2.get("points", 0))
        label = race["raceName"].replace("Grand Prix", "GP")
        race_labels.append(label)
        d1_pts_prog.append(round(d1_total, 1))
        d2_pts_prog.append(round(d2_total, 1))
        positions.append({
            "race": label,
            "d1_pos": int(d1.get("position", 99)),
            "d2_pos": int(d2.get("position", 99)),
            "d1_pts": float(d1.get("points", 0)),
            "d2_pts": float(d2.get("points", 0)),
        })

    return {
        "year": year,
        "driver1": driver1,
        "driver2": driver2,
        "labels": race_labels,
        "d1_points_progression": d1_pts_prog,
        "d2_points_progression": d2_pts_prog,
        "race_positions": positions,
    }


@router.get("/driver-form/{driver_id}")
async def driver_recent_form(driver_id: str, races: int = 5):
    """Recent race form: last N results with points, positions."""
    from datetime import datetime
    year = datetime.now().year
    all_races = await jolpica.get_all_results(year)
    results = []
    for race in all_races:
        for r in race.get("Results", []):
            if r["Driver"]["driverId"] == driver_id:
                results.append({
                    "race": race["raceName"].replace("Grand Prix", "GP"),
                    "round": int(race["round"]),
                    "position": int(r.get("position", 99)),
                    "points": float(r.get("points", 0)),
                    "grid": int(r.get("grid", 0)),
                    "status": r.get("status", ""),
                })
    return {"driver_id": driver_id, "form": results[-races:] if results else []}


@router.get("/predict/{year}/{round_num}")
async def race_predictor(year: int, round_num: int):
    """Simple ML-backed race win probability predictor."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    # Build training data from current season results
    all_races = await jolpica.get_all_results(year)
    X, y = [], []
    for race in all_races:
        if int(race["round"]) >= round_num:
            continue
        for r in race.get("Results", []):
            grid = int(r.get("grid", 20))
            pts = float(r.get("points", 0))
            pos = int(r.get("position", 20))
            won = 1 if pos == 1 else 0
            X.append([grid, pts])
            y.append(won)

    if len(X) < 20:
        return {"error": "Not enough data yet", "predictions": []}

    try:
        X_arr = np.array(X)
        y_arr = np.array(y)
        model = LogisticRegression(max_iter=500)
        model.fit(X_arr, y_arr)

        # Get qualifying result for current round
        quali = await jolpica.get_qualifying_result(year, round_num)
        if not quali:
            return {"error": "No qualifying data yet", "predictions": []}

        qualifying_list = quali.get("QualifyingResults", [])
        predictions = []
        for q in qualifying_list[:10]:
            grid_pos = int(q.get("position", 20))
            driver_id = q["Driver"]["driverId"]
            # Use average points per race this season as second feature
            driver_results = [r for race in all_races for r in race.get("Results", []) if r["Driver"]["driverId"] == driver_id]
            avg_pts = sum(float(r.get("points", 0)) for r in driver_results) / max(len(driver_results), 1)
            prob = model.predict_proba([[grid_pos, avg_pts]])[0][1]
            predictions.append({
                "driver": f"{q['Driver']['givenName']} {q['Driver']['familyName']}",
                "driver_id": driver_id,
                "grid": grid_pos,
                "team": q.get("Constructor", {}).get("name", ""),
                "win_probability": round(float(prob) * 100, 1),
            })

        predictions.sort(key=lambda x: -x["win_probability"])
        return {"year": year, "round": round_num, "predictions": predictions}

    except Exception as e:
        return {"error": str(e), "predictions": []}
