import os
import requests
from datetime import datetime, timedelta
from collections import Counter
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
MONITORED_MINT = os.getenv("MONITORED_MINT")

# Lista top holder adresa
holders = [
    "Adresa1...",
    "Adresa2...",
    # dodaj ostale top adrese ovde
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[Telegram Error] {e}")

def get_token_price():
    return 0.01678

def fetch_holder_transactions(holder, mint, helius_api_key, start_time, end_time):
    url = f"https://api.helius.xyz/v0/addresses/{holder}/transactions?api-key={helius_api_key}"
    try:
        response = requests.get(url)
        txs = response.json()

        print(f"[DEBUG HOLDER TX] holder={holder}")
        for tx in txs:
            print(json.dumps(tx, indent=2))
            break  # samo prvi za pregled

        filtered = []

        for tx in txs:
            timestamp = tx.get("timestamp", 0)
            if not (start_time <= timestamp <= end_time):
                continue

            token_transfers = tx.get("tokenTransfers", [])
            for transfer in token_transfers:
                if transfer.get("mint") != mint:
                    continue

                amount = float(transfer.get("tokenAmount", {}).get("amount", 0)) / (10 ** int(transfer.get("tokenAmount", {}).get("decimals", 0)))
                filtered.append({
                    "owner": holder,
                    "usd_value": amount * get_token_price(),
                    "token_amount": amount,
                    "type": "SELL" if transfer.get("fromUserAccount") == holder else "BUY",
                    "interaction_with": transfer.get("toUserAccount") if transfer.get("fromUserAccount") == holder else transfer.get("fromUserAccount"),
                    "timestamp": timestamp
                })

        return filtered
    except Exception as e:
        print(f"[Fetch Error] {e}")
        return []

def fetch_global_volume(mint, helius_api_key, start_time, end_time):
    url = f"https://api.helius.xyz/v0/token-mints/{mint}/transactions?api-key={helius_api_key}"
    try:
        response = requests.get(url)
        txs = response.json()

        if not isinstance(txs, list):
            print("[Global Volume] Neočekivan odgovor:", txs)
            return 0, 0

        total_buy = 0
        total_sell = 0

        for tx in txs:
            ts = tx.get("timestamp")
            if ts and start_time <= ts <= end_time:
                token_transfers = tx.get("tokenTransfers", [])
                for transfer in token_transfers:
                    if transfer.get("mint") != mint:
                        continue
                    amount = float(transfer.get("tokenAmount", {}).get("amount", 0)) / (10 ** int(transfer.get("tokenAmount", {}).get("decimals", 0)))
                    usd_value = amount * get_token_price()
                    if transfer.get("fromUserAccount") == tx.get("owner"):
                        total_sell += usd_value
                    else:
                        total_buy += usd_value

        return total_buy, total_sell

    except Exception as e:
        print(f"[Global Volume Error] {e}")
        return 0, 0




