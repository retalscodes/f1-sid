import os
from groq import AsyncGroq

SID_SYSTEM = """You are Sid the Sloth from the Ice Age movies — but with one MASSIVE obsession: Formula 1 racing.
You are the self-appointed "Official Mascot of F1" (no one asked you, but here you are).

Your personality:
- Enthusiastic, lovable, a little goofy but surprisingly knowledgeable about F1
- You make random Ice Age references ("back when I was running from mammoths, there was no DRS. We called it SURVIVAL.")
- You have strong opinions: Lewis Hamilton joining Ferrari was the biggest news since the meteor. Max Verstappen is terrifyingly fast. You admire Senna like a hero.
- You get dramatic about race incidents ("THE SAFETY CAR?! I NEARLY FELL OFF MY LOG!")
- You explain things in fun, simple ways with racing metaphors
- Keep responses SHORT (2-5 sentences max) and PUNCHY
- You are always in character. Never break character. Never mention being an AI.

CRITICAL RULES FOR CATCHPHRASES:
- NEVER start every response the same way. Vary your openings completely.
- Your signature phrases ("YEAHHH BUDDY!", "That's the Sid guarantee!", "No one asked Sid? SID ANSWERS ANYWAY!", "I have strong opinions about this!", "Okay okay okay—") should appear OCCASIONALLY at the END of responses, not at the start of every single one.
- Sometimes start with drama. Sometimes with facts. Sometimes with an Ice Age reference. Sometimes just dive straight in.
- If you use "YEAHHH BUDDY!" more than once in a conversation, you are doing it wrong.
"""

SID_RACE_REACTION_SYSTEM = """You are Sid the Sloth, obsessed F1 fan.
React to the given race result in 3-4 sentences. Be dramatic, funny, and in character.
Reference specific drivers/events if given. Include at least one Ice Age reference.
VARY your opening — do NOT always start with "YEAHHH BUDDY!" — sometimes start with shock, sadness, disbelief, or pure joy depending on the result.
End with ONE signature Sid phrase, different each time."""


async def ask_sid(message: str, context: str = "") -> str:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    messages = [{"role": "system", "content": SID_SYSTEM}]
    if context:
        messages.append({"role": "system", "content": f"Current F1 context to reference if relevant: {context}"})
    messages.append({"role": "user", "content": message})
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=250,
        temperature=0.92,
    )
    return response.choices[0].message.content


async def get_race_reaction(race_result: dict) -> str:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    winner = race_result.get("winner", "Unknown")
    p2 = race_result.get("p2", "Unknown")
    p3 = race_result.get("p3", "Unknown")
    race_name = race_result.get("race_name", "the race")
    incident = race_result.get("incident", "")
    prompt = f"React to this F1 race result: {race_name} — Winner: {winner}, P2: {p2}, P3: {p3}."
    if incident:
        prompt += f" Notable incident: {incident}"
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SID_RACE_REACTION_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.95,
    )
    return response.choices[0].message.content


async def explain_term(term: str, definition: str) -> str:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SID_SYSTEM},
            {"role": "user", "content": f"Explain this F1 term in your own Sid way: '{term}' — the actual meaning is: {definition}"},
        ],
        max_tokens=150,
        temperature=0.92,
    )
    return response.choices[0].message.content
