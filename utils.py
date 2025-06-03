import requests
from datetime import datetime
import logging

TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "GtiwjVEQwbaXVkDn7EGteqHwT1KNVxD5XhKMzfgaEKuw",
    "..."  # Dodaj ostale top holdere ovde
]
DEXSCREENER_API = f"https://api.dexscreener.com/latest/dex/pairs/solana/{TOKEN_MINT}"

async def send_telegram_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"[Telegram Error] {e}")

def get_token_price():
    try:
        response = requests.get(DEXSCREENER_API)
        data = response.json()
        return float(data['pair']['priceUsd'])
    except Exception as e:
        logging.error(f"[Greška prilikom dobijanja cene] {e}")
        return 0.0

def fetch_holder_transactions(start_time, end_time):
    # MOCK funkcija - ovde ide pravi kod za fetch transakcija
    return []

def fetch_global_volume(start_time, end_time):
    # MOCK funkcija - ovde ide pravi kod za obradu ukupnih kupovina i prodaja
    return {"buy": 0, "sell": 0}
