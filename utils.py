import httpx
import os
from telegram.constants import ParseMode

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/ayckqvlkmnnqycrch2ffb1xej29nymzc5t6pvyrhackn"

async def get_token_price():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()
            return float(data["pair"]["priceUsd"])
    except Exception as e:
        print(f"[ERROR get_token_price] {e}")
        return 0.0

async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DEXSCREENER_URL)
            data = response.json()["pair"]["volume"]
            txs = response.json()["pair"]["txns"]

            return {
                "buy_volume": float(data["h24"]) * (txs["h24"]["buys"] / (txs["h24"]["buys"] + txs["h24"]["sells"] + 0.001)),
                "sell_volume": float(data["h24"]) * (txs["h24"]["sells"] / (txs["h24"]["buys"] + txs["h24"]["sells"] + 0.001)),
                "change_24h": float(response.json()["pair"]["priceChange"]["h24"])
            }
    except Exception as e:
        print(f"[ERROR fetch_global_volume_delta] {e}")
        return {
            "buy_volume": 0.0,
            "sell_volume": 0.0,
            "change_24h": 0.0
        }

async def send_telegram_message(bot, chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=False)
    except Exception as e:
        print(f"[ERROR send_telegram_message] {e}")
