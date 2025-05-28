import requests
import os
from datetime import datetime

def get_token_price(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        res = requests.get(url, timeout=10)
        data = res.json()
        if "pairs" in data and data["pairs"]:
            return float(data["pairs"][0]["priceUsd"])
    except Exception as e:
        print(f"[!] Greška kod cene: {e}")
    return None


def fetch_holder_transactions(holder, mint, start_ts, end_ts):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{holder}/transactions"
        params = {
            "api-key": os.getenv("HELIUS_API_KEY"),
            "mint": mint,
            "type": "TRANSFER",
            "before": end_ts,
            "after": start_ts,
            "limit": 100
        }
        res = requests.get(url, params=params, timeout=10)
        txs = res.json()
        results = []
        for tx in txs:
            instructions = tx.get("tokenTransfers", [])
            for i in instructions:
                if i.get("mint") == mint and (i.get("fromUser") == holder or i.get("toUser") == holder):
                    if i.get("fromUser") == holder:
                        tx_type = "SELL"
                        counter = i.get("toUser")
                    elif i.get("toUser") == holder:
                        tx_type = "BUY"
                        counter = i.get("fromUser")
                    else:
                        tx_type = "TRANSFER"
                        counter = "?"
                    results.append({
                        "type": tx_type,
                        "timestamp": tx.get("timestamp"),
                        "counterparty": counter
                    })
        return results
    except Exception as e:
        print(f"[!] Greska kod transakcija: {e}")
        return []


def fetch_global_volume(mint, start_ts, end_ts):
    try:
        url = f"https://api.helius.xyz/v0/token/{mint}/transfers"
        params = {
            "api-key": os.getenv("HELIUS_API_KEY"),
            "start": start_ts,
            "end": end_ts,
            "limit": 1000
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        price = get_token_price(mint)
        buy, sell = 0.0, 0.0
        for tx in data:
            delta = int(tx.get("amount", 0)) / (10 ** int(tx.get("decimals", 9)))
            if tx.get("type") == "TRANSFER" and delta:
                if tx.get("fromUser") == tx.get("tokenAccount"):
                    sell += delta * price
                elif tx.get("toUser") == tx.get("tokenAccount"):
                    buy += delta * price
        return round(buy, 2), round(sell, 2)
    except Exception as e:
        print(f"[!] Greska kod globalne analize: {e}")
        return None


def send_telegram_message(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        res = requests.post(url, json=payload, timeout=10)
        print(f"[Telegram] {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[!] Greska kod slanja poruke: {e}")
