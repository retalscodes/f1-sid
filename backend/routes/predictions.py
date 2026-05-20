from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_db
import aiosqlite
import random
import string
from datetime import datetime

router = APIRouter()

POINTS = {"p1_exact": 25, "p2_exact": 18, "p3_exact": 15, "podium_wrong_pos": 6, "fastest_lap": 10}


def gen_code(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


class CreateRoom(BaseModel):
    race_name: str
    race_round: int
    season: int


class JoinPrediction(BaseModel):
    username: str
    p1: str
    p2: str
    p3: str
    fastest_lap: str = ""


class ScoreSubmit(BaseModel):
    actual_p1: str
    actual_p2: str
    actual_p3: str
    actual_fastest_lap: str = ""


@router.post("/room")
async def create_room(body: CreateRoom, db: aiosqlite.Connection = Depends(get_db)):
    code = gen_code()
    await db.execute(
        "INSERT INTO prediction_rooms (code, race_name, race_round, season) VALUES (?, ?, ?, ?)",
        (code, body.race_name, body.race_round, body.season),
    )
    await db.commit()
    return {"code": code, "race_name": body.race_name}


@router.get("/room/{code}")
async def get_room(code: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM prediction_rooms WHERE code = ?", (code.upper(),)) as cur:
        room = await cur.fetchone()
    if not room:
        raise HTTPException(404, "Room not found")
    async with db.execute(
        "SELECT username, p1, p2, p3, fastest_lap, score, submitted_at FROM predictions WHERE room_code = ? ORDER BY score DESC",
        (code.upper(),),
    ) as cur:
        preds = [dict(r) for r in await cur.fetchall()]
    return {**dict(room), "predictions": preds, "count": len(preds)}


@router.post("/room/{code}/predict")
async def submit_prediction(code: str, body: JoinPrediction, db: aiosqlite.Connection = Depends(get_db)):
    code = code.upper()
    async with db.execute("SELECT locked FROM prediction_rooms WHERE code = ?", (code,)) as cur:
        room = await cur.fetchone()
    if not room:
        raise HTTPException(404, "Room not found")
    if room["locked"]:
        raise HTTPException(400, "Predictions locked — race has started!")
    try:
        await db.execute(
            "INSERT INTO predictions (room_code, username, p1, p2, p3, fastest_lap) VALUES (?, ?, ?, ?, ?, ?)",
            (code, body.username, body.p1, body.p2, body.p3, body.fastest_lap),
        )
        await db.commit()
    except Exception:
        raise HTTPException(400, "Username already submitted for this room")
    return {"message": "Prediction submitted!", "username": body.username}


@router.post("/room/{code}/score")
async def score_room(code: str, body: ScoreSubmit, db: aiosqlite.Connection = Depends(get_db)):
    code = code.upper()
    async with db.execute("SELECT * FROM prediction_rooms WHERE code = ?", (code,)) as cur:
        room = await cur.fetchone()
    if not room:
        raise HTTPException(404, "Room not found")
    async with db.execute("SELECT * FROM predictions WHERE room_code = ?", (code,)) as cur:
        preds = [dict(r) for r in await cur.fetchall()]
    podium = [body.actual_p1.lower(), body.actual_p2.lower(), body.actual_p3.lower()]
    for pred in preds:
        score = 0
        p = [pred["p1"].lower(), pred["p2"].lower(), pred["p3"].lower()]
        if p[0] == podium[0]:
            score += POINTS["p1_exact"]
        elif p[0] in podium:
            score += POINTS["podium_wrong_pos"]
        if p[1] == podium[1]:
            score += POINTS["p2_exact"]
        elif p[1] in podium:
            score += POINTS["podium_wrong_pos"]
        if p[2] == podium[2]:
            score += POINTS["p3_exact"]
        elif p[2] in podium:
            score += POINTS["podium_wrong_pos"]
        if pred.get("fastest_lap") and pred["fastest_lap"].lower() == body.actual_fastest_lap.lower():
            score += POINTS["fastest_lap"]
        await db.execute("UPDATE predictions SET score = ? WHERE id = ?", (score, pred["id"]))
    await db.execute("UPDATE prediction_rooms SET locked = 1 WHERE code = ?", (code,))
    await db.commit()
    async with db.execute(
        "SELECT username, p1, p2, p3, fastest_lap, score FROM predictions WHERE room_code = ? ORDER BY score DESC",
        (code,),
    ) as cur:
        results = [dict(r) for r in await cur.fetchall()]
    return {"leaderboard": results, "actual": {"p1": body.actual_p1, "p2": body.actual_p2, "p3": body.actual_p3, "fastest_lap": body.actual_fastest_lap}}


@router.delete("/room/{code}/reset")
async def reset_room(code: str, db: aiosqlite.Connection = Depends(get_db)):
    code = code.upper()
    await db.execute("UPDATE prediction_rooms SET locked = 0 WHERE code = ?", (code,))
    await db.execute("DELETE FROM predictions WHERE room_code = ?", (code,))
    await db.commit()
    return {"message": "Room reset"}
