import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
BASE_URL = f"https://api.helius.xyz/v0"

# Direktno ubačeni holderi
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF",
    # Dodaj ostale adrese ovde
]

TOKEN_MINT = "tvoj_token_mint"


def fetch_holder_transactions(start_time, end_time):
    results = []
    for idx, holder in enumerate(HOLDER_LIST):
        try:
            url = f"{BASE_URL}/addresses/{holder}/transactions?api-key={HELIUS_API_KEY}&limit=50"
            res = requests.get(url)
            data = res.json()

            for tx in data:
                timestamp = tx.get("timestamp")
                if timestamp is None:
                    continue
                dt_object = datetime.utcfromtimestamp(timestamp)
                if not (start_time <= dt_object <= end_time):
                    continue

                for transfer in tx.get("tokenTransfers", []):
                    if transfer.get("mint") == TOKEN_MINT:
                        action = "buy" if transfer.get("toUserAccount") == holder else "sell" if transfer.get("fromUserAccount") == holder else "receive"
                        results.append({
                            "rank": idx + 1,
                            "address": holder,
                            "amount": float(transfer.get("tokenAmount", {}).get("uiAmount", 0)),
                            "action": action,
                            "timestamp": dt_object.strftime("%H:%M")
                        })
        except Exception as e:
            print(f"[Fetch Error] {e}")
    return results


def get_token_price():
    try:
        url = f"https://public-api.birdeye.so/public/price?address={TOKEN_MINT}"
        res = requests.get(url)
        data = res.json()
        return float(data.get("data", {}).get("value", 0))
    except Exception as e:
        print(f"[Price Error] {e}")
        return 0


def fetch_global_volume(start_time, end_time):
    total_buy = 0
    total_sell = 0
    try:
        url = f"https://api.helius.xyz/v0/tokens/{TOKEN_MINT}/transactions?api-key={HELIUS_API_KEY}&limit=100"
        res = requests.get(url)
        data = res.json()

        for tx in data:
            timestamp = tx.get("timestamp")
            if timestamp is None:
                continue
            dt_object = datetime.utcfromtimestamp(timestamp)
            if not (start_time <= dt_object <= end_time):
                continue

            for transfer in tx.get("tokenTransfers", []):
                amount = float(transfer.get("tokenAmount", {}).get("uiAmount", 0))
                if amount == 0:
                    continue

                sender = transfer.get("fromUserAccount")
                receiver = transfer.get("toUserAccount")
                if sender in HOLDER_LIST:
                    total_sell += amount * get_token_price()
                elif receiver in HOLDER_LIST:
                    total_buy += amount * get_token_price()
    except Exception as e:
        print(f"[Volume Error] {e}")
    return {"buy": total_buy, "sell": total_sell}


def send_telegram_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        print(f"[Telegram Error] {e}")




