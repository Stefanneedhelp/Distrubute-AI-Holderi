import os
import logging
from datetime import datetime, timedelta
import httpx
from telegram import Bot
import dateutil.parser

# Postavljanje osnovnih vrednosti
API_KEY = "a8032eda-b022-48d7-aca8-7cc37f02cf25"
TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
DEX_PAIR_ID = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2",
    "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
]

logging.basicConfig(level=logging.INFO)

async def send_telegram_message(bot: Bot, chat_id: str, text: str):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

def fetch_token_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR_ID}"
        response = httpx.get(url)
        data = response.json()
        return float(data["pair"]["priceUsd"])
    except Exception as e:
        logging.warning(f"[Price Error] {e}")
        return 0.0

def fetch_holder_transactions(start_time, end_time):
    results = []
    for rank, address in enumerate(HOLDER_LIST, start=1):
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={API_KEY}"
            response = httpx.get(url)
            transactions = response.json()
            for tx in transactions:
                try:
                    ts = tx.get("timestamp")
                    if isinstance(ts, str):
                        tx_time = dateutil.parser.isoparse(ts)
                    elif isinstance(ts, int):
                        tx_time = datetime.utcfromtimestamp(ts)
                    else:
                        continue

                    if not (start_time <= tx_time <= end_time):
                        continue

                    # Ovo možeš dodatno podesiti prema payload strukturi
                    action = "buy" if "buy" in tx["description"].lower() else "sell" if "sell" in tx["description"].lower() else "transfer"
                    amount = tx.get("amount", 0)
                    results.append({
                        "rank": rank,
                        "address": address,
                        "action": action,
                        "amount": amount,
                        "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    logging.warning(f"[Fetch Error] Holder {rank} – {e}")
                    continue
        except Exception as e:
            logging.warning(f"[Fetch Error] Holder {rank} – {e}")
    return results

def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token/{TOKEN_MINT}/transfers?api-key={API_KEY}"
        response = httpx.get(url)
        transfers = response.json()

        total_buy = 0
        total_sell = 0

        for tx in transfers:
            try:
                ts = tx.get("timestamp")
                if isinstance(ts, str):
                    tx_time = dateutil.parser.isoparse(ts)
                elif isinstance(ts, int):
                    tx_time = datetime.utcfromtimestamp(ts)
                else:
                    continue

                if not (start_time <= tx_time <= end_time):
                    continue

                if "buy" in tx.get("description", "").lower():
                    total_buy += tx.get("amount", 0)
                elif "sell" in tx.get("description", "").lower():
                    total_sell += tx.get("amount", 0)
            except Exception as e:
                logging.warning(f"[Volume Error - Single Tx] {e}")
                continue

        return {"buy": total_buy, "sell": total_sell}

    except Exception as e:
        logging.warning(f"[Volume Error] {e}")
        return {"buy": 0, "sell": 0}



