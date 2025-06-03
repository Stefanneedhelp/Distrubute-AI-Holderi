import requests
import os
from datetime import datetime, timedelta

# Lista holder adresa direktno u kodu
HOLDERS = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "6eT6tdrCxKZKGHkNok9wGWz8DJEnN1FfAWkjLpbLpgHj",
    "DsCJ5siuJT8vqKkQCVWyBLemzPp2G9Jfpx9n3GRgBdEv",
    # Dodaj ostale adrese ovde
]

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
MONITORED_MINT = os.getenv("MONITORED_MINT")

# Funkcija za slanje poruke

def send_telegram_message(bot, chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

# Fetch cena tokena sa Dexscreener API-ja

def get_token_price():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/ayckqvavbjdhvky3evwvngz0a62xwqtxuyat6adpknka"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        return float(data["pair"]["priceUsd"])
    except Exception as e:
        print("[Fetch Error - Price]", e)
        return 0.0

# Fetch globalne kupovine i prodaje

def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token-metadata?api-key={HELIUS_API_KEY}"
        buy = 0
        sell = 0
        # Napomena: ovde bi u idealnom slučaju koristili endpoint za history transakcije
        # i parsirali tipove po interakcijama sa AMM poolovima
        return {"buy": buy, "sell": sell}
    except Exception as e:
        print("[Global Volume Error]", e)
        return {"buy": 0, "sell": 0}

# Fetch transakcije top holdera

def fetch_holder_transactions(start_time, end_time):
    results = []
    headers = {"Content-Type": "application/json"}

    for idx, holder in enumerate(HOLDERS, 1):
        try:
            url = f"https://api.helius.xyz/v0/addresses/{holder}/transactions?api-key={HELIUS_API_KEY}"
            res = requests.get(url, headers=headers)
            txs = res.json()

            for tx in txs:
                ts = tx.get("timestamp")
                if not ts:
                    continue

                timestamp_dt = datetime.utcfromtimestamp(ts)
                if not (start_time <= timestamp_dt <= end_time):
                    continue

                amount = 0
                action = "transfer"
                partner = "N/A"

                for t in tx.get("tokenTransfers", []):
                    if t.get("mint") != MONITORED_MINT:
                        continue
                    amount = abs(float(t["tokenAmount"]["tokenAmount"]))
                    if t["toUserAccount"] == holder:
                        action = "buy"
                        partner = t["fromUserAccount"]
                    elif t["fromUserAccount"] == holder:
                        action = "sell"
                        partner = t["toUserAccount"]

                results.append({
                    "address": holder,
                    "rank": idx,
                    "timestamp": timestamp_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": amount,
                    "action": action,
                    "partner": partner
                })
        except Exception as e:
            print("[Fetch Error]", e)

    return results






