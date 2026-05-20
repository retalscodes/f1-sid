from fastapi import APIRouter
from pydantic import BaseModel
from services.sid_ai import ask_sid, get_race_reaction, explain_term
from services import jolpica
from datetime import datetime

router = APIRouter()


class ChatMessage(BaseModel):
    message: str


class RaceReactionRequest(BaseModel):
    winner: str
    p2: str
    p3: str
    race_name: str
    incident: str = ""


class GlossaryRequest(BaseModel):
    term: str
    definition: str


async def _build_context() -> str:
    try:
        year = datetime.now().year
        standings = await jolpica.get_driver_standings(year)
        leader = standings[0] if standings else {}
        leader_name = f"{leader.get('Driver', {}).get('givenName', '')} {leader.get('Driver', {}).get('familyName', '')}"
        leader_pts = leader.get("points", "?")
        schedule = await jolpica.get_schedule(year)
        now = datetime.now().isoformat()[:10]
        next_races = [r for r in schedule if r.get("date", "") >= now]
        next_race = next_races[0].get("raceName", "upcoming race") if next_races else "end of season"
        return f"Current F1 {year} season. Championship leader: {leader_name} with {leader_pts} pts. Next race: {next_race}."
    except Exception:
        return f"F1 {datetime.now().year} season is underway."


@router.post("/ask")
async def ask(body: ChatMessage):
    context = await _build_context()
    reply = await ask_sid(body.message, context)
    return {"reply": reply}


@router.post("/reaction")
async def race_reaction(body: RaceReactionRequest):
    reply = await get_race_reaction(body.dict())
    return {"reaction": reply}


@router.post("/glossary")
async def glossary_explain(body: GlossaryRequest):
    reply = await explain_term(body.term, body.definition)
    return {"explanation": reply}
