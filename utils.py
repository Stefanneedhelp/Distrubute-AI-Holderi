import os
import requests
from datetime import datetime, timedelta
from collections import Counter

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
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[Telegram Error] {e}")

def get_token_price():
    return 0.01678

def fetch_holder_transactions(holder, mint, helius_api_key, start_time, end_time):
    url = f"https://api.helius.xyz/v0/addresses/{holder}/transactions?api-key={helius_api_key}&mint={mint}&type=TRANSFER"
    try:
        response = requests.get(url)
        txs = response.json()
        filtered = []
        for tx in txs:
            timestamp = tx.get("timestamp", 0)
            if start_time <= timestamp <= end_time:
                filtered.append({
                    "owner": holder,
                    "usd_value": float(tx.get("tokenValue", 0)) * get_token_price(),
                    "type": "BUY" if tx.get("tokenStandard") == "fungible" else "SELL",
                    "interaction_with": tx.get("tokenAccount", "N/A"),
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
                amount = float(tx.get("tokenValue", 0)) * get_token_price()
                if tx.get("type") == "BUY":
                    total_buy += amount
                elif tx.get("type") == "SELL":
                    total_sell += amount

        return total_buy, total_sell

    except Exception as e:
        print(f"[Global Volume Error] {e}")
        return 0, 0

def send_daily_report():
    now = datetime.utcnow()
    start_time = int((now - timedelta(days=1)).timestamp())
    end_time = int(now.timestamp())
    token_price = get_token_price()

    all_transactions = []
    for holder in holders:
        txs = fetch_holder_transactions(holder, MONITORED_MINT, HELIUS_API_KEY, start_time, end_time)
        all_transactions.extend(txs)

    total_buy = sum(tx["usd_value"] for tx in all_transactions if tx["type"] == "BUY")
    total_sell = sum(tx["usd_value"] for tx in all_transactions if tx["type"] == "SELL")
    ratio = round(total_buy / total_sell, 2) if total_sell > 0 else "∞"

    if not all_transactions:
        report = f"""📊 Dnevni izveštaj ({now.strftime('%Y-%m-%d %H:%M')})
Cena: ${token_price:.6f}

Ukupno kupljeno: $0.00
Ukupno prodato: $0.00
Odnos kupovina/prodaja: 0.00

📭 <b>Nema aktivnosti holdera</b>
"""
        send_telegram_message(report)
        return

    address_counts = Counter(tx["owner"] for tx in all_transactions)
    most_active_holder, max_count = address_counts.most_common(1)[0]

    report = f"""📊 Dnevni izveštaj ({now.strftime('%Y-%m-%d %H:%M')})
Cena: ${token_price:.6f}

Ukupno kupljeno: ${total_buy:,.2f}
Ukupno prodato: ${total_sell:,.2f}
Odnos kupovina/prodaja: {ratio}

🔁 Broj transakcija holdera: {len(all_transactions)}
🔥 Najaktivniji holder: {most_active_holder} ({max_count} transakcije)
"""

    send_telegram_message(report)


