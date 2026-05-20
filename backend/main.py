from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()

from database import init_db
from routes import races, live, history, championship, circuits, chat, predictions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="SID's F1 Hub", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(races.router, prefix="/api/races", tags=["races"])
app.include_router(live.router, prefix="/api/live", tags=["live"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(championship.router, prefix="/api/championship", tags=["championship"])
app.include_router(circuits.router, prefix="/api/circuits", tags=["circuits"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])

# On Render, Netlify serves the frontend — only mount locally
if not os.getenv("RENDER"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
