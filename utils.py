import os
import httpx
from telegram.constants import ParseMode

# ✅ Dexscreener URL
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/ayckqvlkmnnqycrch2ffb1xej29nymzc5t6pvyrhackn"

# ✅ RPC URL i MINT iz ENV
RPC_URL = os.getenv("RPC_URL")
DIS_MINT_ADDRESS = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"  # DIS token mint

if not RPC_URL:
    raise ValueError("RPC_URL nije postavljen! Proveri .env ili Render environment variables.")

# ✅ Dobijanje cene tokena
async def get_token_price():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()
            return float(data["pair"]["priceUsd"])
    except Exception as e:
        print(f"[ERROR get_token_price] {e}")
        return 0.0

# ✅ Dobijanje volumena i promene cene
async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()

            volume = float(data["pair"]["volume"]["h24"])
            txs = data["pair"]["txns"]["h24"]
            buys = txs["buys"]
            sells = txs["sells"]
            total = buys + sells + 0.001  # da ne podelimo sa nulom

            return {
                "buy_volume": volume * (buys / total),
                "sell_volume": volume * (sells / total),
                "change_24h": float(data["pair"]["priceChange"]["h24"])
            }
    except Exception as e:
        print(f"[ERROR fetch_global_volume_delta] {e}")
        return {
            "buy_volume": 0.0,
            "sell_volume": 0.0,
            "change_24h": 0.0
        }

# ✅ RPC poziv
async def call_rpc(payload):
    headers = {"Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(RPC_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            if response.text.strip() == "":
                raise ValueError("RPC response je prazan!")

            return response.json()
    except Exception as e:
        wallet = payload.get("params", ["?"])[0]
        print(f"[ERROR holder check] {wallet}: {e}")
        return None

# ✅ Dobijanje balansa za jednog holdera
async def get_dis_balance(wallet_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {
                "mint": DIS_MINT_ADDRESS
            },
            {
                "encoding": "jsonParsed"
            }
        ]
    }

    data = await call_rpc(payload)
    if not data:
        return 0.0

    try:
        accounts = data["result"]["value"]
        total = 0.0
        for acc in accounts:
            amount = float(acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"])
            total += amount
        print(f"[DEBUG] {wallet_address} balans: {total}")
        return total
    except Exception as e:
        print(f"[ERROR get_dis_balance] {wallet_address}: {e}")
        return 0.0

# ✅ Slanje poruke na Telegram
async def send_telegram_message(bot, chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
    except Exception as e:
        print(f"[ERROR send_telegram_message] {e}")
