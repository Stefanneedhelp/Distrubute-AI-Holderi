import requests
from datetime import datetime, timedelta
import os

# DexScanner token ID i adrese
TOKEN_MINT = "introvert1qyfq9ewyxgsu5qurtnu39ndv0a"
HOLDER_ADDRESSES = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "9zEHbnVZEVFcsmZ4z4PYNxnJhKrN3bNUvNfsYqSz2yLG",
    "F5i9Zh1LkpQUo9Bphwh1V4JmdsV2s5xvsCFSjxXFSvqG",
    # Dodaj ostale adrese ovde...
]

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"


def send_telegram_message(bot, chat_id, text):
    try:
        response = requests.post(TELEGRAM_API_URL, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
        response.raise_for_status()
    except Exception as e:
        print(f"[Telegram Error] {e}")


def get_token_price():
    try:
        url = f"https://public-api.dexscreener.com/latest/dex/pairs/solana/{TOKEN_MINT}"
        response = requests.get(url)
        data = response.json()
        return float(data['pair']['priceUsd'])
    except Exception as e:
        print(f"[Fetch Error] Price: {e}")
        return 0.0


def fetch_holder_transactions(start_time, end_time):
    results = []
    for i, address in enumerate(HOLDER_ADDRESSES):
        try:
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={os.getenv('HELIUS_API_KEY')}"
            response = requests.get(url)
            txs = response.json()

            for tx in txs:
                timestamp = tx.get("timestamp")
                if timestamp:
                    tx_time = datetime.utcfromtimestamp(timestamp)
                    if not (start_time <= tx_time <= end_time):
                        continue

                    action = "unknown"
                    amount = 0

                    # Proveravamo tokenTransfers
                    for transfer in tx.get("tokenTransfers", []):
                        if transfer.get("mint") == TOKEN_MINT:
                            if transfer.get("toUserAccount") == address:
                                action = "buy"
                            elif transfer.get("fromUserAccount") == address:
                                action = "sell"
                            amount = round(float(transfer.get("tokenAmount", {}).get("userAmount", 0)), 2)

                    if action != "unknown" and amount > 0:
                        results.append({
                            "rank": i + 1,
                            "address": address,
                            "action": action,
                            "amount": amount,
                            "timestamp": tx_time.strftime("%H:%M")
                        })
        except Exception as e:
            print(f"[Fetch Error] {e}")
    return results


def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token-transfers?api-key={os.getenv('HELIUS_API_KEY')}"
        response = requests.post(url, json={
            "mint": TOKEN_MINT,
            "start": int(start_time.timestamp()),
            "end": int(end_time.timestamp()),
            "limit": 1000
        })
        data = response.json()

        buy = 0
        sell = 0

        for tx in data:
            amount = float(tx.get("tokenAmount", {}).get("userAmount", 0))
            if tx.get("type") == "TRANSFER" and amount > 0:
                if tx.get("toUserAccount") in HOLDER_ADDRESSES:
                    buy += amount
                elif tx.get("fromUserAccount") in HOLDER_ADDRESSES:
                    sell += amount

        price = get_token_price()
        return {
            "buy": buy * price,
            "sell": sell * price
        }
    except Exception as e:
        print(f"[Fetch Error] Global volume: {e}")
        return {"buy": 0.0, "sell": 0.0}
