import os
import logging
import requests
import httpx
import dateutil.parser
from datetime import datetime
from telegram import Bot

# Konstante
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
TOKEN_ADDRESS = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
DEX_PAIR_ID = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
HOLDERS = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2",
    "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
]

# Telegram slanje poruke
async def send_telegram_message(bot: Bot, chat_id: str, text: str):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

# Cena tokena preko Dexscreener-a
def get_token_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR_ID}"
        res = httpx.get(url).json()
        return float(res["pair"]["priceUsd"])
    except Exception as e:
        logging.warning(f"[Price Error] {e}")
        return 0.0

# Volume kupovina/prodaja svih adresa u 1h
def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token/{TOKEN_ADDRESS}/transfers?api-key={HELIUS_API_KEY}"
        res = httpx.get(url).json()

        buy_usd = 0.0
        sell_usd = 0.0
        price = get_token_price()

        for tx in res:
            ts = dateutil.parser.isoparse(tx["timestamp"])
            if not (start_time <= ts <= end_time):
                continue

            amount = int(tx["tokenAmount"]["amount"]) / (10 ** int(tx["tokenAmount"]["decimals"]))
            direction = tx.get("type")
            if direction == "TRANSFER" and tx.get("source") == "SWAP":
                if tx["tokenAmount"]["owner"] == tx["toUserAccount"]:
                    buy_usd += amount * price
                else:
                    sell_usd += amount * price

        ratio = buy_usd / sell_usd if sell_usd != 0 else 0
        return {"buy": buy_usd, "sell": sell_usd, "ratio": ratio}

    except Exception as e:
        logging.warning(f"[Volume Error] {e}")
        return {"buy": 0.0, "sell": 0.0, "ratio": 0.0}

# Aktivnosti holdera
async def fetch_holder_transactions(start_time, end_time):
    results = []

    for idx, address in enumerate(HOLDERS, start=1):
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}"
            res = httpx.get(url).json()

            for tx in res:
                ts = dateutil.parser.isoparse(tx["timestamp"])
                if not (start_time <= ts <= end_time):
                    continue

                action = "transfer"
                amount = 0
                for change in tx.get("tokenTransfers", []):
                    if change.get("mint") == TOKEN_ADDRESS:
                        amount = int(change["tokenAmount"]["tokenAmount"])
                        if change["toUserAccount"] == address:
                            action = "buy"
                        elif change["fromUserAccount"] == address:
                            action = "sell"
                        break

                results.append({
                    "rank": idx,
                    "address": address,
                    "action": action,
                    "amount": amount,
                    "timestamp": ts.strftime("%Y-%m-%d %H:%M")
                })
        except Exception as e:
            logging.warning(f"[Fetch Error] Holder {idx} – {e}")
            continue

    return results



