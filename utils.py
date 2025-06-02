import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEX_API = "https://api.dexscreener.com/latest/dex/pairs/solana/"
MINT_ADDRESS = os.getenv("MONITORED_MINT")
HOLDER_LIST = os.getenv("HOLDER_LIST").split(",")  # lista adresa razdvojena zarezima

def fetch_holder_transactions(start_time, end_time):
    try:
        response = requests.get(os.getenv("WEBHOOK_URL"))
        data = response.json()

        transactions = data if isinstance(data, list) else [data]
        holder_actions = []

        for tx in transactions:
            tx_time = datetime.utcfromtimestamp(tx["timestamp"])
            if not (start_time <= tx_time <= end_time):
                continue

            for transfer in tx.get("nativeTransfers", []):
                from_addr = transfer.get("fromUserAccount")
                to_addr = transfer.get("toUserAccount")

                if from_addr in HOLDER_LIST or to_addr in HOLDER_LIST:
                    action = None
                    holder_address = from_addr if from_addr in HOLDER_LIST else to_addr

                    if from_addr in HOLDER_LIST and to_addr not in HOLDER_LIST:
                        action = "sell"
                    elif to_addr in HOLDER_LIST and from_addr not in HOLDER_LIST:
                        action = "buy"
                    else:
                        action = "transfer"

                    holder_actions.append({
                        "rank": HOLDER_LIST.index(holder_address) + 1,
                        "address": holder_address,
                        "amount": transfer["amount"] / 1e9,
                        "timestamp": tx_time.strftime("%H:%M"),
                        "action": action
                    })

        return holder_actions
    except Exception as e:
        logging.error(f"[Greška u fetch_holder_transactions] {e}")
        return []

def fetch_global_volume(start_time, end_time):
    try:
        response = requests.get(os.getenv("WEBHOOK_URL"))
        data = response.json()

        transactions = data if isinstance(data, list) else [data]
        total_buy = 0
        total_sell = 0
        activity_counter = {}

        for tx in transactions:
            tx_time = datetime.utcfromtimestamp(tx["timestamp"])
            if not (start_time <= tx_time <= end_time):
                continue

            for transfer in tx.get("nativeTransfers", []):
                from_addr = transfer.get("fromUserAccount")
                to_addr = transfer.get("toUserAccount")

                if from_addr in HOLDER_LIST:
                    total_sell += transfer["amount"] / 1e9
                    activity_counter[from_addr] = activity_counter.get(from_addr, 0) + 1
                elif to_addr in HOLDER_LIST:
                    total_buy += transfer["amount"] / 1e9
                    activity_counter[to_addr] = activity_counter.get(to_addr, 0) + 1

        most_active = max(activity_counter.items(), key=lambda x: x[1])[0] if activity_counter else None

        return {
            "buy": total_buy,
            "sell": total_sell,
            "most_active": most_active
        }
    except Exception as e:
        logging.error(f"[Greška u fetch_global_volume] {e}")
        return {"buy": 0, "sell": 0, "most_active": None}

def get_token_price():
    try:
        response = requests.get(DEX_API + MINT_ADDRESS)
        data = response.json()
        return float(data["pairs"][0]["priceUsd"])
    except Exception as e:
        logging.error(f"[Greška u get_token_price] {e}")
        return 0.0

def send_telegram_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"[Greška u slanju poruke] {e}")




