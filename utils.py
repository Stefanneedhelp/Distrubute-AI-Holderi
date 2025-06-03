import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HELIUS_API_KEY")
TOKEN_MINT = os.getenv("MONITORED_TOKEN")

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Direktno unete adrese holdera
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "GtiwjVEQwbaXVkDn7EGteqHwT1KNVxD5XhKMzfgaEKuw",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    # Dodaj ostale adrese po potrebi
]


def fetch_holder_transactions(start_time, end_time):
    holder_activity = []

    for rank, address in enumerate(HOLDER_LIST, start=1):
        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={API_KEY}"

        try:
            response = requests.get(url, headers=HEADERS)
            data = response.json()

            for tx in data:
                timestamp = datetime.utcfromtimestamp(tx["timestamp"])
                if not (start_time <= timestamp <= end_time):
                    continue

                for transfer in tx.get("tokenTransfers", []):
                    if transfer["mint"] != TOKEN_MINT:
                        continue

                    action = "buy" if transfer["toUserAccount"] == address else "sell" if transfer["fromUserAccount"] == address else "receive"

                    holder_activity.append({
                        "rank": rank,
                        "address": address,
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": float(transfer["tokenAmount"]["uiAmount"]),
                        "action": action
                    })
        except Exception as e:
            print(f"[Fetch Error] {e}")

    return holder_activity


def get_token_price():
    try:
        res = requests.get(f"https://public-api.birdeye.so/public/price?address={TOKEN_MINT}", headers=HEADERS)
        return float(res.json()["data"]["value"])
    except:
        return 0.0


def fetch_global_volume(start_time, end_time):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{TOKEN_MINT}"

    try:
        res = requests.get(url)
        data = res.json()["pair"]
        buys = float(data.get("volume", {}).get("h1BuyUsd", 0))
        sells = float(data.get("volume", {}).get("h1SellUsd", 0))
        return {"buy": buys, "sell": sells}
    except:
        return {"buy": 0, "sell": 0}


def send_telegram_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"[Telegram Error] {e}")




