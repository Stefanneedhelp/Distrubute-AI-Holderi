# === utils.py ===
import os
import requests
import httpx
import logging
from datetime import datetime
from dateutil import parser

TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
DEX_PAIR = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
HOLDERS = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2",
    "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
]

API_KEY = os.getenv("HELIUS_API_KEY")

async def send_telegram_message(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

def get_token_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR}"
        res = requests.get(url).json()
        return float(res['pair']['priceUsd'])
    except Exception as e:
        logging.warning(f"[Price Error] {e}")
        return 0.0

def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token/{TOKEN_MINT}/transfers?api-key={API_KEY}"
        res = requests.get(url).json()

        buy_usd = 0
        sell_usd = 0
        for tx in res:
            timestamp = parser.isoparse(tx["timestamp"])
            if start_time <= timestamp <= end_time:
                amount = float(tx["tokenAmount"]) * float(tx.get("tokenPrice", 0))
                if tx.get("type") == "BUY":
                    buy_usd += amount
                elif tx.get("type") == "SELL":
                    sell_usd += amount
        ratio = buy_usd / sell_usd if sell_usd else 0
        return {"buy": buy_usd, "sell": sell_usd, "ratio": ratio}
    except Exception as e:
        logging.warning(f"[Volume Error] {e}")
        return {"buy": 0, "sell": 0, "ratio": 0}

async def fetch_holder_transactions(start_time, end_time):
    result = []
    for i, holder in enumerate(HOLDERS, 1):
        try:
            url = f"https://api.helius.xyz/v0/addresses/{holder}/transactions?api-key={API_KEY}"
            res = await httpx.AsyncClient().get(url)
            data = res.json()
            for tx in data:
                timestamp = parser.isoparse(tx["timestamp"])
                if not (start_time <= timestamp <= end_time):
                    continue

                action = "receive" if tx.get("type") == "TRANSFER" else "buy" if "buy" in tx.get("description", "").lower() else "sell"
                result.append({
                    "rank": i,
                    "address": holder,
                    "action": action,
                    "amount": round(tx.get("nativeTransfers", [{}])[0].get("amount", 0) / 1e9, 4),
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M')
                })
                break
        except Exception as e:
            logging.warning(f"[Fetch Error] Holder {i} – {e}")
    return result



