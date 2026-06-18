import asyncio
import json
import time
from pathlib import Path
from typing import Any

import fastf1
import pandas as pd

CACHE_DIR = Path("fastf1_cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

_mem_cache: dict[str, tuple[Any, float]] = {}


def _cached(key: str, ttl: int = 86400) -> Any | None:
    if key in _mem_cache:
        val, ts = _mem_cache[key]
        if time.time() - ts < ttl:
            return val
    return None


def _store(key: str, val: Any) -> None:
    _mem_cache[key] = (val, time.time())


def _lap_seconds(td) -> float | None:
    try:
        return td.total_seconds()
    except Exception:
        return None


def _load_race_laps(year: int, round_num: int) -> dict:
    key = f"laps_{year}_{round_num}"
    cached = _cached(key)
    if cached:
        return cached
    session = fastf1.get_session(year, round_num, "R")
    session.load(telemetry=False, weather=False, messages=False)
    laps = session.laps
    result = {}
    for drv in laps["Driver"].unique():
        drv_laps = laps[laps["Driver"] == drv].copy()
        records = []
        for _, row in drv_laps.iterrows():
            lt = _lap_seconds(row.get("LapTime"))
            if lt and 60 < lt < 200:
                records.append({
                    "lap": int(row["LapNumber"]),
                    "time": round(lt, 3),
                    "compound": str(row.get("Compound", "")),
                    "tyre_life": int(row.get("TyreLife", 0)) if pd.notna(row.get("TyreLife")) else 0,
                    "is_pb": bool(row.get("IsPersonalBest", False)),
                })
        result[drv] = records
    _store(key, result)
    return result


def _load_quali_laps(year: int, round_num: int) -> dict:
    key = f"quali_{year}_{round_num}"
    cached = _cached(key)
    if cached:
        return cached
    session = fastf1.get_session(year, round_num, "Q")
    session.load(telemetry=False, weather=False, messages=False)
    laps = session.laps.pick_fastest()
    result = {}
    for drv in session.laps["Driver"].unique():
        drv_laps = session.laps[session.laps["Driver"] == drv]
        best = drv_laps.pick_fastest()
        if best is not None and not best.empty:
            lt = _lap_seconds(best.get("LapTime"))
            s1 = _lap_seconds(best.get("Sector1Time"))
            s2 = _lap_seconds(best.get("Sector2Time"))
            s3 = _lap_seconds(best.get("Sector3Time"))
            result[drv] = {
                "lap_time": lt,
                "s1": round(s1, 3) if s1 else None,
                "s2": round(s2, 3) if s2 else None,
                "s3": round(s3, 3) if s3 else None,
                "compound": str(best.get("Compound", "")),
            }
    _store(key, result)
    return result


async def get_lap_comparison(year: int, round_num: int, d1: str, d2: str) -> dict:
    loop = asyncio.get_event_loop()
    try:
        all_laps = await loop.run_in_executor(None, _load_race_laps, year, round_num)
        return {
            "driver1": {"abbr": d1, "laps": all_laps.get(d1, [])},
            "driver2": {"abbr": d2, "laps": all_laps.get(d2, [])},
            "year": year,
            "round": round_num,
        }
    except Exception as e:
        return {"error": str(e)}


async def get_tire_strategy(year: int, round_num: int) -> dict:
    loop = asyncio.get_event_loop()
    try:
        all_laps = await loop.run_in_executor(None, _load_race_laps, year, round_num)
        strategy = {}
        for drv, laps in all_laps.items():
            stints = []
            if not laps:
                continue
            current = {"compound": laps[0]["compound"], "start": laps[0]["lap"], "end": laps[0]["lap"]}
            for lap in laps[1:]:
                if lap["compound"] == current["compound"]:
                    current["end"] = lap["lap"]
                else:
                    stints.append(current)
                    current = {"compound": lap["compound"], "start": lap["lap"], "end": lap["lap"]}
            stints.append(current)
            strategy[drv] = stints
        return {"strategy": strategy, "year": year, "round": round_num}
    except Exception as e:
        return {"error": str(e)}


async def get_quali_comparison(year: int, round_num: int, d1: str, d2: str) -> dict:
    loop = asyncio.get_event_loop()
    try:
        quali = await loop.run_in_executor(None, _load_quali_laps, year, round_num)
        return {
            "driver1": {"abbr": d1, **quali.get(d1, {})},
            "driver2": {"abbr": d2, **quali.get(d2, {})},
        }
    except Exception as e:
        return {"error": str(e)}


async def get_available_rounds(year: int) -> list[dict]:
    loop = asyncio.get_event_loop()
    try:
        def _load():
            schedule = fastf1.get_event_schedule(year, include_testing=False)
            rounds = []
            for _, row in schedule.iterrows():
                rounds.append({
                    "round": int(row["RoundNumber"]),
                    "name": str(row["EventName"]),
                    "country": str(row.get("Country", "")),
                    "date": str(row["EventDate"])[:10],
                })
            return rounds
        return await loop.run_in_executor(None, _load)
    except Exception as e:
        return []
