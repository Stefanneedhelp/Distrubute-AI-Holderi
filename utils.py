import os
import httpx
from telegram import Bot

# Dexscreener pair za DIS token na Solani
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/ayckqvlkmnnqycrch2ffb1xej29nymzc5t6pvyrhackn"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ✅ Funkcija: Dohvatanje cene DIS tokena
async def get_token_price():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()

            if data and "pair" in data and "priceUsd" in data["pair"]:
                return float(data["pair"]["priceUsd"])

            print("[ERROR get_token_price] Unexpected API response:", data)
            return None
    except Exception as e:
        print(f"[ERROR get_token_price] {e}")
        return None

# ✅ Funkcija: Dohvatanje kupovina i prodaja za 24h
async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()

            if data and "pair" in data and "volume" in data["pair"]:
                volume_data = data["pair"]["volume"]
                buy_volume = float(volume_data.get("buy", 0))
                sell_volume = float(volume_data.get("sell", 0))

                return {
                    "buy_volume": buy_volume,
                    "sell_volume": sell_volume,
                    "change_24h": buy_volume - sell_volume
                }

            print("[ERROR fetch_global_volume_delta] Unexpected API response:", data)
            return None
    except Exception as e:
        print(f"[ERROR fetch_global_volume_delta] {e}")
        return None

# ✅ Funkcija: Slanje poruke na Telegram
async def send_telegram_message(bot: Bot, chat_id: str, message: str):
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        print(f"[ERROR send_telegram_message] {e}")

# ✅ Funkcija: Dohvatanje balansa DIS tokena koristeći Alchemy RPC
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
            data = response.json()

            value = data.get("result", {}).get("value", [])
            if not value:
                return 0.0

            amount = value[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
            return float(amount)

    except Exception as e:
        print(f"[ERROR get_dis_balance] {address}: {e}")
        return 0.0
