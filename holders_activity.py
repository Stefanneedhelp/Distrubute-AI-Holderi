import json
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ✅ Zamena RPC URL-a
RPC_URL = "https://rpc.ankr.com/solana"

# ✅ Top 5 adresa (hardkodovano)
TOP_5 = [
    "7MTiWyDsjNYDWXmZ3J331bz6zwJrJ416ipR8oif42q5D",
    "E5WchutHdCY8besK1gFg8Bc5AzXssZeDPKrNGWemiip",
    "2y66QqQNVzC9321h9shfndZxH3eqdwmMSP2EMuitBJG2",
    "8ExkZcutpGMYLLJbQYCWTShHkLvjgTrk7GkqNank3Jag",
    "2DoQ7aikEF3GS1AGp7fBqnCTGmoLV8VhiJDmRLZEjyqM"
]

MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
STATE_PATH = "state.json"
DIS_THRESHOLD = 10_000  # 10k DIS prag

async def get_dis_balance(address: str) -> float:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            address,
            {"mint": MINT},
            {"encoding": "jsonParsed"}
        ]
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(RPC_URL, json=payload)
        if r.status_code != 200 or not r.text.startswith("{"):
            print(f"[ERROR] Nevalidan RPC odgovor za {address}: {r.text[:100]}")
            return 0.0
        try:
            data = r.json()
            ui_amount = data["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
            return float(ui_amount)
        except Exception as e:
            print(f"[ERROR] Greska za {address}: {e}")
            return 0.0

def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, data=payload)

async def check_balances():
    state = load_state()
    changes = []

    for address in TOP_5:
        current_balance = await get_dis_balance(address)
        previous = state.get(address, 0)
        delta = current_balance - previous

        if abs(delta) >= DIS_THRESHOLD:
            direction = "📥 Povećanje" if delta > 0 else "📤 Smanjenje"
            msg = (
                f"🚨 <b>Promena balansa za holder</b>\n"
                f"📍 Adresa: <code>{address}</code>\n"
                f"📦 Novi balans: {current_balance:,.2f} DIS\n"
                f"📊 Promena: {delta:+,.2f} DIS\n"
                f"{direction}"
            )
            changes.append(msg)

        state[address] = current_balance  # ažuriraj za sledeći krug

    save_state(state)

    for msg in changes:
        await send_telegram_message(msg)

# Ovo pozivaš iz glavnog loop-a na svakih 5 minuta
if __name__ == "__main__":
    import asyncio
    asyncio.run(check_balances())
