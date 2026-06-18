from fastapi import APIRouter
from services import jolpica
from services.weather import CIRCUITS, get_circuit_weather

router = APIRouter()

CIRCUIT_FACTS = {
    "bahrain": {
        "lap_record": "1:31.447 — Pedro de la Rosa (2005)",
        "length_km": 5.412, "turns": 15, "drs_zones": 3, "first_gp": 2004,
        "fun_fact": "Built in the desert with air-cooled tarmac. The track hosts races under floodlights to avoid peak daytime heat.",
        "overtaking_difficulty": "Good. Three DRS zones and long straights make for genuine racing.",
        "sid_quote": "Racing in the desert at night! Sand, lights, heat — I survived an ice age so I respect this commitment to extreme conditions.",
    },
    "saudi_arabia": {
        "lap_record": "1:27.653 — Lewis Hamilton (2021)",
        "length_km": 6.174, "turns": 27, "drs_zones": 3, "first_gp": 2021,
        "fun_fact": "The second-longest circuit on the calendar and one of the fastest street circuits ever designed.",
        "overtaking_difficulty": "Surprisingly good — long straights and three DRS zones despite the walls everywhere.",
        "sid_quote": "Twenty-seven corners and walls EVERYWHERE. I counted. Twice. My heart rate went up just watching. That's impressive for a sloth.",
    },
    "australia": {
        "lap_record": "1:19.813 — Charles Leclerc (2024)",
        "length_km": 5.278, "turns": 16, "drs_zones": 3, "first_gp": 1996,
        "fun_fact": "Albert Park is a semi-permanent circuit around a public park — locals jog those same roads the other 51 weekends of the year.",
        "overtaking_difficulty": "Moderate. Long back straight and safety cars typically shake up the order.",
        "sid_quote": "The Australian GP opens the season every year! The excitement, the drama, and apparently kangaroos nearby which I find personally relatable.",
    },
    "japan": {
        "lap_record": "1:30.983 — Lewis Hamilton (2019)",
        "length_km": 5.807, "turns": 18, "drs_zones": 1, "first_gp": 1987,
        "fun_fact": "The only figure-8 circuit on the F1 calendar, featuring a unique crossover bridge section.",
        "overtaking_difficulty": "Difficult but rewarding. Spoon Curve and 130R are legendary corners.",
        "sid_quote": "A figure-8 track?! Even my mammoth friends couldn't draw that in the snow. Genius humans!",
    },
    "china": {
        "lap_record": "1:32.238 — Michael Schumacher (2004)",
        "length_km": 5.451, "turns": 16, "drs_zones": 2, "first_gp": 2004,
        "fun_fact": "Turn 14 hairpin with a 1.2km run-in is one of the best overtaking opportunities on the entire calendar.",
        "overtaking_difficulty": "Good. DRS on the back straight produces reliable overtakes at the hairpin.",
        "sid_quote": "Shanghai has the best hairpin for overtaking. Teams plot for LAPS setting it up. Strategy within strategy. My kind of complex, slow plan.",
    },
    "miami": {
        "lap_record": "1:29.708 — Max Verstappen (2023)",
        "length_km": 5.412, "turns": 19, "drs_zones": 3, "first_gp": 2022,
        "fun_fact": "Runs around the Hard Rock Stadium. The iconic fake marina section has become a symbol of F1's American expansion.",
        "overtaking_difficulty": "Decent. Long back straight and DRS zones plus the Turn 17 complex offer good battles.",
        "sid_quote": "Miami has a fake marina and real palm trees and an ENORMOUS stadium. The vibes are immaculate. Even this sloth felt glamorous.",
    },
    "emilia_romagna": {
        "lap_record": "1:15.484 — Max Verstappen (2022)",
        "length_km": 4.909, "turns": 19, "drs_zones": 1, "first_gp": 2020,
        "fun_fact": "Named after Enzo Ferrari and his son Dino — it sits in the heart of the Italian Motor Valley, surrounded by Ferrari, Lamborghini and Ducati.",
        "overtaking_difficulty": "Hard. Tight layout with limited passing spots — tyre strategy and timing are everything.",
        "sid_quote": "Imola is in Ferrari country. The Tifosi walk here from their homes. This circuit has SOUL. Named after Enzo Ferrari which is basically royalty.",
    },
    "monaco": {
        "lap_record": "1:12.909 — Lewis Hamilton (2021)",
        "length_km": 3.337, "turns": 19, "drs_zones": 1, "first_gp": 1950,
        "fun_fact": "The swimming pool section is literally next to a public swimming pool. Glamour and absurdity in equal measure.",
        "overtaking_difficulty": "Nearly impossible on track. Qualifying position and strategy decide everything.",
        "sid_quote": "Monaco is like trying to run through my ice cave without knocking anything over. IMPOSSIBLE but beautiful!",
    },
    "canada": {
        "lap_record": "1:13.078 — Valtteri Bottas (2019)",
        "length_km": 4.361, "turns": 14, "drs_zones": 2, "first_gp": 1978,
        "fun_fact": "The Wall of Champions at the chicane has claimed Damon Hill, Michael Schumacher, and Jacques Villeneuve — all within the same weekend.",
        "overtaking_difficulty": "Good. The hairpin and long pit straight produce genuine overtakes every race.",
        "sid_quote": "The Wall of Champions has eaten THREE world champions in one weekend. That wall is more successful than most drivers. Very impressive wall.",
    },
    "spain": {
        "lap_record": "1:16.330 — Max Verstappen (2023)",
        "length_km": 4.675, "turns": 14, "drs_zones": 2, "first_gp": 1991,
        "fun_fact": "Teams use Catalunya for pre-season testing more than any other circuit — by race week, every team knows it inside out.",
        "overtaking_difficulty": "Moderate. The long main straight and DRS help but the circuit is well-understood.",
        "sid_quote": "Every team tests here so much that there are literally no secrets at Barcelona. It's F1's homework circuit. Everybody passes the test differently.",
    },
    "austria": {
        "lap_record": "1:05.619 — Carlos Sainz (2020)",
        "length_km": 4.318, "turns": 10, "drs_zones": 3, "first_gp": 1970,
        "fun_fact": "The Red Bull Ring sits in the stunning Styrian Alps at 700m elevation — one of the most scenic circuits on the calendar.",
        "overtaking_difficulty": "Excellent. Short lap, elevation changes, and three DRS zones make for frantic racing.",
        "sid_quote": "Mountains! Elevation changes! Red Bull's HOME! The atmosphere here is electric and the views are magnificent. Even Scrat would have loved this terrain.",
    },
    "britain": {
        "lap_record": "1:27.097 — Max Verstappen (2020)",
        "length_km": 5.891, "turns": 18, "drs_zones": 2, "first_gp": 1950,
        "fun_fact": "Copse corner is taken at nearly 300 km/h flat out. Silverstone hosted the very first Formula 1 World Championship race in 1950.",
        "overtaking_difficulty": "Moderate. Vale complex and the Wellington Straight provide the best chances.",
        "sid_quote": "Copse at full speed?! Even I wouldn't attempt that, and I survived the Ice Age!",
    },
    "belgium": {
        "lap_record": "1:41.252 — Valtteri Bottas (2018)",
        "length_km": 7.004, "turns": 19, "drs_zones": 2, "first_gp": 1950,
        "fun_fact": "Eau Rouge / Raidillon is considered the most iconic corner sequence in motorsport. It's genuinely flat out in a modern F1 car.",
        "overtaking_difficulty": "Good. The Kemmel Straight is one of the best overtaking opportunities in F1.",
        "sid_quote": "Spa in the rain is CHAOS. I once slid down a glacier in similar conditions. Did not end well.",
    },
    "hungary": {
        "lap_record": "1:16.627 — Lewis Hamilton (2020)",
        "length_km": 4.381, "turns": 14, "drs_zones": 2, "first_gp": 1986,
        "fun_fact": "Known as 'Monaco without the glamour' — the track is tight, twisty and almost impossible to overtake on without strategy.",
        "overtaking_difficulty": "Very difficult. Turn 1 after the straight and pit strategy are the main levers.",
        "sid_quote": "Hungaroring. Where overtaking goes to die but strategy THRIVES. It's basically chess at 300 km/h. I love chess. Slowly.",
    },
    "netherlands": {
        "lap_record": "1:11.097 — Lewis Hamilton (2021)",
        "length_km": 4.259, "turns": 14, "drs_zones": 2, "first_gp": 1952,
        "fun_fact": "Zandvoort features banked corners (up to 18°) — a concept from 1950s design that makes it unique on the modern calendar.",
        "overtaking_difficulty": "Hard. Banking speeds things up but the narrow track limits passing to Turn 1.",
        "sid_quote": "ORANGE ARMY. The Dutch fans are absolutely unhinged in the best possible way. They built an entire party nation around Max. Respect.",
    },
    "italy": {
        "lap_record": "1:21.046 — Rubens Barrichello (2004)",
        "length_km": 5.793, "turns": 11, "drs_zones": 2, "first_gp": 1950,
        "fun_fact": "The Temple of Speed — highest average lap speeds on the F1 calendar. Low-downforce trim means cars look completely different here.",
        "overtaking_difficulty": "Excellent. Slipstreaming into the chicanes produces multiple overtakes per lap.",
        "sid_quote": "Monza is pure SPEED. Even a sloth would be fast here. Well... maybe not THIS sloth.",
    },
    "azerbaijan": {
        "lap_record": "1:43.009 — Charles Leclerc (2023)",
        "length_km": 6.003, "turns": 20, "drs_zones": 2, "first_gp": 2017,
        "fun_fact": "The castle section winds through Baku's 12th-century Old City — a UNESCO World Heritage Site. Cars race between 800-year-old walls.",
        "overtaking_difficulty": "Great. The 2.2km main straight sees cars hit over 360 km/h — the longest DRS zone in F1.",
        "sid_quote": "Baku has ancient castle walls AND a 2km straight where cars do 360 km/h. Built in the 12th century. Going fast in the 21st. Wild concept.",
    },
    "singapore": {
        "lap_record": "1:35.867 — Lewis Hamilton (2023)",
        "length_km": 4.940, "turns": 19, "drs_zones": 3, "first_gp": 2008,
        "fun_fact": "The only permanent night race — 1,500+ floodlights illuminate the circuit. It's also consistently the hottest race for drivers inside the cockpit.",
        "overtaking_difficulty": "Difficult. Tight street circuit, but safety cars and pit windows regularly shuffle positions.",
        "sid_quote": "Night race through a lit-up city! I am nocturnal and this speaks to me. The lights, the humidity, the drama at every corner. PERFECTION.",
    },
    "usa": {
        "lap_record": "1:36.169 — Charles Leclerc (2019)",
        "length_km": 5.513, "turns": 20, "drs_zones": 2, "first_gp": 2012,
        "fun_fact": "COTA was designed by a German architect with specific homages to other F1 circuits — Turn 2 mirrors Silverstone's Maggotts section.",
        "overtaking_difficulty": "Good. Turn 1 uphill into a long braking zone is one of the world's best overtaking spots.",
        "sid_quote": "COTA was DESIGNED with F1 fans in mind. Turn 1 uphill is SPECTACULAR. Americans built something genuinely special here.",
    },
    "mexico": {
        "lap_record": "1:17.774 — Valtteri Bottas (2021)",
        "length_km": 4.304, "turns": 17, "drs_zones": 3, "first_gp": 1963,
        "fun_fact": "At 2,285m above sea level, Mexico City's thin air forces teams to run more wing angle than any other venue to maintain downforce.",
        "overtaking_difficulty": "Good. Stadium section provides atmosphere, long straight and DRS deliver overtakes.",
        "sid_quote": "Altitude! Thin air! Teams spend months calculating this one event. The fan atmosphere is also thin but absolutely ELECTRIC. Go figure.",
    },
    "brazil": {
        "lap_record": "1:10.540 — Rubens Barrichello (2004)",
        "length_km": 4.309, "turns": 15, "drs_zones": 2, "first_gp": 1973,
        "fun_fact": "Interlagos runs anti-clockwise — drivers are pushed right in high-speed corners instead of left, creating unusual physical demands on the neck.",
        "overtaking_difficulty": "Excellent. The Senna S and the main pit straight produce real, classic overtakes.",
        "sid_quote": "Brazil! Interlagos! The home of Ayrton Senna. The passion here is IMMENSE. Anti-clockwise circuit too — my neck hurts watching in the right direction.",
    },
    "las_vegas": {
        "lap_record": "1:35.490 — Oscar Piastri (2024)",
        "length_km": 6.201, "turns": 17, "drs_zones": 2, "first_gp": 2023,
        "fun_fact": "Runs through the Las Vegas Strip past iconic hotels — the main straight past the Bellagio is nearly 2km long, the longest DRS zone in F1.",
        "overtaking_difficulty": "Good. Three long straights, cold night temperatures and DRS create unpredictable racing.",
        "sid_quote": "Las Vegas at NIGHT on the Strip with 2km of DRS. The most American thing F1 has ever done and I respect the total commitment to chaos.",
    },
    "qatar": {
        "lap_record": "1:24.319 — Max Verstappen (2023)",
        "length_km": 5.380, "turns": 16, "drs_zones": 2, "first_gp": 2021,
        "fun_fact": "Lusail was a MotoGP circuit before F1 arrived — its smooth, sweeping high-speed layout was an instant hit with drivers.",
        "overtaking_difficulty": "Moderate. High-speed corners make close following tough but DRS zones compensate.",
        "sid_quote": "Lusail has incredible high-speed sweepers that look terrifying from onboard. Teams suffer badly with tyre degradation here. Sloth pace strongly recommended.",
    },
    "abu_dhabi": {
        "lap_record": "1:26.103 — Max Verstappen (2021)",
        "length_km": 5.281, "turns": 16, "drs_zones": 2, "first_gp": 2009,
        "fun_fact": "Yas Marina is the season finale venue — the race starts at sunset and finishes under full floodlights as day turns to night.",
        "overtaking_difficulty": "Moderate. The 2021 layout redesign improved it massively from the old 'processional' circuit.",
        "sid_quote": "The season finale. Sun sets, lights come on, the championship may be decided here. Abu Dhabi 2021 still haunts me. We don't discuss it. 🦥",
    },
}

CIRCUIT_ERGAST_IDS = {
    "bahrain": "bahrain",
    "saudi_arabia": "jeddah",
    "australia": "albert_park",
    "japan": "suzuka",
    "china": "shanghai",
    "miami": "miami",
    "emilia_romagna": "imola",
    "monaco": "monaco",
    "canada": "villeneuve",
    "spain": "catalunya",
    "austria": "red_bull_ring",
    "britain": "silverstone",
    "belgium": "spa",
    "hungary": "hungaroring",
    "netherlands": "zandvoort",
    "italy": "monza",
    "azerbaijan": "baku",
    "singapore": "marina_bay",
    "usa": "americas",
    "mexico": "rodriguez",
    "brazil": "interlagos",
    "las_vegas": "vegas",
    "qatar": "losail",
    "abu_dhabi": "yas_marina",
}


@router.get("/")
async def list_circuits():
    return [{"key": k, **v} for k, v in CIRCUITS.items()]


@router.get("/{circuit_key}")
async def circuit_dna(circuit_key: str):
    circuit = CIRCUITS.get(circuit_key)
    if not circuit:
        return {"error": "Circuit not found"}
    facts = CIRCUIT_FACTS.get(circuit_key, {})
    weather = {}
    try:
        weather = await get_circuit_weather(circuit_key)
    except Exception:
        pass
    winners = await get_circuit_winners(circuit_key)
    return {
        "key": circuit_key,
        **circuit,
        **facts,
        "weather": weather,
        "past_winners": winners[:10],
    }


async def get_circuit_winners(circuit_key: str) -> list:
    ergast_id = CIRCUIT_ERGAST_IDS.get(circuit_key)
    if not ergast_id:
        return []
    try:
        import httpx
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                f"https://api.jolpi.ca/ergast/f1/circuits/{ergast_id}/results/1.json?limit=30"
            )
            data = r.json()
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return [
            {
                "year": race["season"],
                "winner": f"{race['Results'][0]['Driver']['givenName']} {race['Results'][0]['Driver']['familyName']}",
                "constructor": race["Results"][0]["Constructor"]["name"],
                "time": race["Results"][0].get("Time", {}).get("time", ""),
            }
            for race in sorted(races, key=lambda x: x["season"], reverse=True)
            if race.get("Results")
        ]
    except Exception:
        return []
