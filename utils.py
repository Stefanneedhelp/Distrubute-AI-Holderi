import requests
import os
from datetime import datetime
import asyncio

from telegram import Bot

# Token mint i Helius URL
TOKEN_MINT = "6uRkfcMtuNkeqGfttVn9dMgFjPtPk1CRWGb6cwgbUgtR"  # zameni ako je drugačiji
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
HELIUS_URL = f"https://mainnet.helius.xyz/v0"

# Direktno ubačena lista holder adresa
HOLDER_LIST = [
    "GtiwjVEQwbaXVkDn7EGteqHwT1KNVxD5XhKMzfgaEKuw",
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "E5WchutHdCY8besK1gFg8Bc5AzXssZeDPKrNGWWemiiP",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF",
    # dodaj još ako imaš
]

# Parsiranje transakcija holdera
def fetch_holder_transactions(start_time, end_time):
    result = []
    for rank, holder in enumerate(HOLDER_LIST, start=1):
        url = f"{HELIUS_URL}/addresses/{holder}/transactions?api-key={HELIUS_API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
        except Exception as e:
            print(f"[Fetch Error] {e}")
            continue

        for tx in data:
            timestamp = datetime.utcfromtimestamp(tx.get("timestamp", 0))
            if not (start_time <= timestamp <= end_time):
                continue

            for transfer in tx.get("tokenTransfers", []):
                if transfer.get("mint") != TOKEN_MINT:
                    continue
                amount = transfer.get("tokenAmount", 0)
                if amount == 0:
                    continue

                action = (
                    "buy" if transfer.get("toUserAccount") == holder else
                    "sell" if transfer.get("fromUserAccount") == holder else
                    "receive"
                )

                result.append({
                    "rank": rank,
                    "address": holder,
                    "amount": amount,
                    "timestamp": timestamp.strftime("%H:%M:%S"),
                    "action": action,
                })
                break
    return result

# Procenjena cena tokena
def get_token_price():
    try:
        url = f"https://public-api.birdeye.so/public/price?address={TOKEN_MINT}"
        headers = {"X-API-KEY": "birdeye_public_api_key"}  # zameni ako koristiš tvoj key
        res = requests.get(url, headers=headers).json()
        return res["data"]["value"]
    except Exception as e:
        print(f"[Price Error] {e}")
        return 0.0

# Ukupno kupljeno i prodato u USD
def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{TOKEN_MINT}"
        res = requests.get(url).json()
        pairs = res.get("pairs", [])
        if not pairs:
            return {"buy": 0, "sell": 0}
        volume = pairs[0].get("volume", {})
        return {
            "buy": float(volume.get("h1", {}).get("buy", 0)),
            "sell": float(volume.get("h1", {}).get("sell", 0)),
        }
    except Exception as e:
        print(f"[Volume Error] {e}")
        return {"buy": 0, "sell": 0}

# Slanje poruke na Telegram
def send_telegram_message(bot: Bot, chat_id: str, text: str):
    try:
        asyncio.run(bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown"))
    except Exception as e:
        print(f"[Send Error] {e}")
