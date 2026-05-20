# 🦥 SID'S F1 HUB

The unofficial sloth's guide to Formula 1. Live data, predictions with friends, full history, and Sid's hot takes.

---

## ⚡ Quick Start

### 1. Get a free Groq API key
Go to [console.groq.com](https://console.groq.com) → Sign up (free) → Create API Key → copy it.

### 2. Set up the backend
```bash
cd f1-sid/backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file
copy .env.example .env
# Open .env and paste your Groq API key
```

### 3. Run it
```bash
# From inside f1-sid/backend/ with venv active:
uvicorn main:app --reload --port 8000
```

Open your browser at **http://localhost:8000** — done!

---

## 📁 Project Structure

```
f1-sid/
├── backend/
│   ├── main.py              ← FastAPI app entry point
│   ├── database.py          ← SQLite setup (predictions rooms)
│   ├── requirements.txt
│   ├── .env                 ← Your GROQ_API_KEY goes here
│   ├── services/
│   │   ├── openf1.py        ← Live race data (free, no key)
│   │   ├── jolpica.py       ← Historical F1 data (free, no key)
│   │   ├── sid_ai.py        ← Sid chatbot via Groq/Llama
│   │   └── weather.py       ← Circuit weather via Open-Meteo (free)
│   └── routes/
│       ├── races.py         ← Schedule, countdown, next race
│       ├── live.py          ← Live session positions/stints/radio
│       ├── history.py       ← Seasons, teams, drivers, H2H
│       ├── championship.py  ← Standings, battle tracker
│       ├── circuits.py      ← Circuit DNA, past winners
│       ├── chat.py          ← Sid chat + glossary + reactions
│       └── predictions.py   ← Friend rooms, scoring, leaderboard
└── frontend/
    ├── index.html           ← Home: countdown, standings, last race
    ├── assets/
    │   ├── css/main.css     ← Full design system (red F1 theme)
    │   ├── js/
    │   │   ├── api.js       ← All API calls in one place
    │   │   ├── app.js       ← Homepage logic
    │   │   ├── countdown.js ← Race countdown + start lights
    │   │   └── sid-chat.js  ← Sid chat bubble
    │   └── img/
    │       └── sid.png      ← Drop Sid's image here! (see below)
    └── pages/
        ├── live.html        ← Live dashboard (positions, stints, radio)
        ├── predictions.html ← Friend prediction rooms
        ├── history.html     ← Season / team / driver explorer
        ├── head-to-head.html← Driver vs driver comparison
        ├── circuit.html     ← Circuit DNA profiles
        ← quiz.html          ← "What F1 team are you?" quiz
        ├── glossary.html    ← F1 terms explained by Sid
        └── silly-season.html← Driver transfer tracker
```

---

## 🦥 Add Sid's Face

Drop any image of Sid (like the Red Bull cap meme!) into:
```
frontend/assets/img/sid.png
```
It will appear in the hero section, nav logo, and chat bubble automatically.
If no image is found, it falls back to the 🦥 emoji (still great).

---

## 🌐 APIs Used (All Free)

| API | What it does | Key needed? |
|-----|-------------|-------------|
| [OpenF1](https://openf1.org) | Live race data, positions, stints, radio | No |
| [Jolpica/Ergast](https://api.jolpi.ca) | Full F1 history since 1950 | No |
| [Open-Meteo](https://open-meteo.com) | Circuit weather forecasts | No |
| [Groq](https://console.groq.com) | Sid chatbot (Llama 3.3 70B) | Yes (free) |

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Countdown Timer** | Animated countdown to next race with start lights |
| **Live Dashboard** | Real-time positions, tire strategy, race control, team radio |
| **Race Predictions** | Create rooms with a code, share with friends, score after the race |
| **Championship Tracker** | Driver & constructor standings with visual bar charts |
| **History Explorer** | Browse by season, team, or driver — back to 1950 |
| **Head to Head** | Compare any two drivers across a full season |
| **Circuit DNA** | Track profiles, weather, records, past winners |
| **What Team Are You?** | 8-question Sid personality quiz |
| **F1 Glossary** | 27 terms explained by Sid in character |
| **Silly Season** | 2025 driver transfer tracker with Sid's reactions |
| **Sid Chat** | Ask Sid anything about F1, he answers as himself |

---

## 🏎️ Sharing With Friends

To share the site with friends on your local network:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Then share your local IP: `http://192.168.x.x:8000`

For public hosting, deploy to **Railway**, **Render**, or **Fly.io** (all have free tiers).
Set the `GROQ_API_KEY` environment variable in your hosting dashboard.

---

*Sid would like to remind you this is unofficial and he did NOT consult with FIA before building this.*
