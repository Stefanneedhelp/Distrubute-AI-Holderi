import requests
from datetime import datetime
import os

def fetch_holder_transactions(holder, mint, helius_api_key, start_time, end_time):
    return []

def get_token_price(mint_address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_address}"
        response = requests.get(url)
        data = response.json()
        if "pairs" in data and len(data["pairs"]) > 0:
            return float(data["pairs"][0]["priceUsd"])
    except Exception as e:
        print(f"❌ Greška u dohvatanju cene: {e}")
    return 0.0

def fetch_global_volume(mint, helius_api_key, start_time, end_time):
    return (0.0, 0.0)

def send_telegram_message(message):
    telegram_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload)
        print(f"✅ Poruka poslata: {response.status_code}")
    except Exception as e:
        print(f"❌ Greška u slanju poruke: {e}")

