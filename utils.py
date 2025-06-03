import os
import httpx
import logging
from datetime import datetime
from dateutil import parser

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"

TOKEN_ADDRESS = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
PAIR_ID = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2",
    "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf",
]

logger = logging.getLogger(__name__)

def fetch_holder_transactions(start_time, end_time):
    headers = {"accept": "application/json"}
    base_url = f"https://api.helius.xyz/v0/addresses"
    all_txns = []

    for idx, address in enumerate(HOLDER_LIST):
        url = f"{base_url}/{address}/transactions?api-key={HELIUS_API_KEY}"
        try:
            response = httpx.get(url, headers=headers)
            data = response.json()
            for tx in data:
                try:
                    ts = parser.parse(tx["timestamp"])
                    if not (start_time <= ts <= end_time):
                        continue
                    for event in tx.get("tokenTransfers", []):
                        if event["mint"] == TOKEN_ADDRESS:
                            action = "buy" if event["toUserAccount"] == address else "sell" if event["fromUserAccount"] == address else "transfer"
                            all_txns.append({
                                "rank": idx + 1,
                                "address": address,
                                "action": action,
                                "amount": event["tokenAmount"],
                                "timestamp": ts.strftime("%H:%M:%S")
                            })
                except Exception as e:
                    logger.warning(f"[Fetch Error] Holder {idx+1} – {e}")
        except Exception as e:
            logger.warning(f"[Fetch Error] Holder {idx+1} – {e}")

    return all_txns

def get_token_price():
    try:
        url = f"{DEXSCREENER_URL}/{PAIR_ID}"
        response = httpx.get(url)
        data = response.json()
        return float(data["pair"]["priceUsd"])
    except Exception as e:
        logger.warning(f"[Price Error] {e}")
        return 0.0

def fetch_global_volume(start_time, end_time):
    url = f"https://api.helius.xyz/v0/token/{TOKEN_ADDRESS}/transfers?api-key={HELIUS_API_KEY}"
    try:
        response = httpx.get(url)
        data = response.json()
        buy_total = 0
        sell_total = 0
        for tx in data:
            try:
                ts = parser.parse(tx["timestamp"])
                if not (start_time <= ts <= end_time):
                    continue
                if tx["type"] == "TRANSFER":
                    if tx["source"] in HOLDER_LIST:
                        sell_total += tx["tokenAmount"]
                    elif tx["destination"] in HOLDER_LIST:
                        buy_total += tx["tokenAmount"]
            except Exception as e:
                continue
        return {"buy": buy_total, "sell": sell_total}
    except Exception as e:
        logger.warning(f"[Volume Error] {e}")
        return {"buy": 0, "sell": 0}

def send_telegram_message(bot, chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"[Telegram Error] {e}")




