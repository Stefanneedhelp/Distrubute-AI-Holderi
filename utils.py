import os
import httpx
import pytz
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
DEX_PAIR_ID = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2",
    "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
]

async def send_telegram_message(bot, chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

def parse_timestamp(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def fetch_holder_transactions(start_time, end_time):
    headers = {"accept": "application/json"}
    results = []

    for idx, address in enumerate(HOLDER_LIST):
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}"
            r = httpx.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()

            for tx in data:
                try:
                    ts = parse_timestamp(tx["timestamp"])
                    if not (start_time <= ts <= end_time):
                        continue

                    for token in tx.get("tokenTransfers", []):
                        if token.get("mint") != TOKEN_MINT:
                            continue

                        amount = float(token.get("amount", 0))
                        sender = token.get("fromUserAccount")
                        recipient = token.get("toUserAccount")

                        if sender == address:
                            action = "sell"
                        elif recipient == address:
                            action = "buy"
                        else:
                            action = "receive"

                        results.append({
                            "rank": idx + 1,
                            "address": address,
                            "amount": amount,
                            "action": action,
                            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    logging.warning(f"[Fetch Error] Holder {idx + 1} – {e}")
        except Exception as e:
            logging.warning(f"[Fetch Error] Holder {idx + 1} – {e}")

    return results

def get_token_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR_ID}"
        r = httpx.get(url)
        r.raise_for_status()
        return float(r.json()["pair"]["priceUsd"])
    except Exception as e:
        logging.warning(f"[Price Error] {e}")
        return 0.0

def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token/{TOKEN_MINT}/transfers?api-key={HELIUS_API_KEY}"
        r = httpx.get(url)
        r.raise_for_status()
        data = r.json()

        buy_total = 0.0
        sell_total = 0.0

        for tx in data:
            ts = parse_timestamp(tx["timestamp"])
            if not (start_time <= ts <= end_time):
                continue

            amount = float(tx.get("amount", 0))
            buyer = tx.get("toUserAccount")
            seller = tx.get("fromUserAccount")

            if buyer and buyer not in HOLDER_LIST:
                buy_total += amount
            if seller and seller not in HOLDER_LIST:
                sell_total += amount

        return {"buy": buy_total, "sell": sell_total}
    except Exception as e:
        logging.warning(f"[Volume Error] {e}")
        return {"buy": 0.0, "sell": 0.0}



