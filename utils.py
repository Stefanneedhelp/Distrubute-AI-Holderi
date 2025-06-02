import os
import requests
from datetime import datetime
from holders import HOLDERS

def send_telegram_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
    except Exception as e:
        print(f"[Telegram Error] {e}")

def get_token_price():
    # Dummy return, replace with actual API call if needed
    return 0.01678

def fetch_global_volume(start_time, end_time):
    # Dummy return, replace with real data if needed
    return {"buy": 0.0, "sell": 0.0}

def fetch_holder_transactions(start_time, end_time):
    results = []
    for idx, address in enumerate(HOLDERS):
        # Example dummy logic (replace with real API calls)
        txs = []  # Replace with actual fetch logic
        for tx in txs:
            ts = datetime.utcfromtimestamp(tx["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            results.append({
                "rank": idx + 1,
                "address": address,
                "action": tx.get("type", "unknown"),
                "amount": tx.get("amount", 0),
                "timestamp": ts
            })
    return results




