import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TELEGRAM_API_URL = "https://api.telegram.org/bot"
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Učitaj holder liste iz fajla
with open("holders.txt", "r") as f:
    HOLDER_LIST = [line.strip() for line in f if line.strip()]

TOKEN_MINT = os.getenv("MONITORED_MINT")
DEX_SCANNER_URL = f"https://public-api.dexscreener.com/latest/dex/pairs/solana/{TOKEN_MINT}"


def fetch_holder_transactions(start_time, end_time):
    url = os.getenv("HELIUS_URL")
    results = []

    for address in HOLDER_LIST:
        response = requests.post(url, json={
            "query": {
                "account": address,
                "start": int(start_time.timestamp()),
                "end": int(end_time.timestamp()),
                "limit": 100
            }
        })
        data = response.json()
        if isinstance(data, dict):
            transactions = data.get("transactions", [])
            for tx in transactions:
                tx_type = "buy" if "buy" in tx.get("description", "").lower() else "sell" if "sell" in tx.get("description", "").lower() else "receive"
                results.append({
                    "address": address,
                    "rank": HOLDER_LIST.index(address) + 1,
                    "action": tx_type,
                    "amount": round(float(tx.get("amount", 0)), 2),
                    "timestamp": datetime.utcfromtimestamp(tx.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M")
                })
    return results


def get_token_price():
    try:
        res = requests.get(DEX_SCANNER_URL)
        data = res.json()
        return float(data["pair"]["priceUsd"])
    except:
        return 0.0


def fetch_global_volume(start_time, end_time):
    url = os.getenv("HELIUS_URL")
    total_buy = 0.0
    total_sell = 0.0

    for address in HOLDER_LIST:
        response = requests.post(url, json={
            "query": {
                "account": address,
                "start": int(start_time.timestamp()),
                "end": int(end_time.timestamp()),
                "limit": 100
            }
        })
        data = response.json()
        if isinstance(data, dict):
            transactions = data.get("transactions", [])
            for tx in transactions:
                desc = tx.get("description", "").lower()
                amount = float(tx.get("amount", 0))
                if "buy" in desc:
                    total_buy += amount
                elif "sell" in desc:
                    total_sell += amount

    return {"buy": total_buy, "sell": total_sell}


def send_telegram_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)






