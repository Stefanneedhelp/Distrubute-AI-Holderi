import os
import httpx
from telegram import Bot

# ✅ Ispravan Dexscreener URL sa validnim pair ID
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ✅ Formatiranje velikih brojeva (npr. 113400000 -> 113.4M)
def format_number(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    else:
        return str(round(n))

# ✅ Dohvatanje cene tokena
async def get_token_price():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)

            if response.status_code != 200:
                print(f"[ERROR get_token_price] Status code: {response.status_code}")
                return None

            data = response.json()

            if not data or "pair" not in data or not data["pair"]:
                print(f"[ERROR get_token_price] Invalid response format: {data}")
                return None

            return float(data["pair"]["priceUsd"])

    except Exception as e:
        print(f"[ERROR get_token_price] {e}")
        return None

# ✅ Dohvatanje volumena kupovina/prodaja
async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)

            if response.status_code != 200:
                print(f"[ERROR fetch_global_volume_delta] Status code: {response.status_code}")
                return None

            data = response.json()

            if not data or "pair" not in data or "volume" not in data["pair"]:
                print(f"[ERROR fetch_global_volume_delta] Invalid response format: {data}")
                return None

            volume_data = data["pair"]["volume"]
            buy_volume = float(volume_data.get("buy", 0))
            sell_volume = float(volume_data.get("sell", 0))

            return {
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
                "change_24h": buy_volume - sell_volume
            }

    except Exception as e:
        print(f"[ERROR fetch_global_volume_delta] {e}")
        return None

# ✅ Slanje poruke na Telegram
async def send_telegram_message(bot: Bot, chat_id: str, message: str):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"[ERROR send_telegram_message] {e}")

# ✅ Dohvatanje DIS balansa koristeći Alchemy RPC
async def get_dis_balance(address: str):
    try:
        ALCHEMY_RPC_URL = os.getenv("ALCHEMY_RPC_URL")
        MINT = os.getenv("DIS_MINT_ADDRESS")

        if not ALCHEMY_RPC_URL or not MINT:
            print("[ERROR get_dis_balance] Missing env variables.")
            return 0.0

        headers = {"Content-Type": "application/json"}
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
            response = await client.post(ALCHEMY_RPC_URL, json=payload, headers=headers)

            if response.status_code != 200:
                print(f"[ERROR get_dis_balance] Status code: {response.status_code}")
                return 0.0

            data = response.json()
            value = data.get("result", {}).get("value", [])

            if not value:
                print(f"[DEBUG get_dis_balance] No token accounts for {address}")
                return 0.0

            amount = value[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
            return float(amount)

    except Exception as e:
        print(f"[ERROR get_dis_balance] {address}: {e}")
        return 0.0
