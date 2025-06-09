import os
import httpx
from telegram import Bot

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/ayckqvlkmnnqycrch2ffb1xej29nymzc5t6pvyrhackn"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()

            if data and "pair" in data and "volume" in data["pair"]:
                volume_data = data["pair"]["volume"]
                buy_volume = float(volume_data.get("buy", 0))
                sell_volume = float(volume_data.get("sell", 0))
                return buy_volume, sell_volume

            print("[ERROR fetch_global_volume_delta] Unexpected API response:", data)
            return None
    except Exception as e:
        print(f"[ERROR fetch_global_volume_delta] {e}")
        return None

async def send_telegram_message(message: str):
    try:
        async with Bot(token=BOT_TOKEN) as bot:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        print(f"[ERROR send_telegram_message] {e}")
