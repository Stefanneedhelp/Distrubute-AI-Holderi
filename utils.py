import requests
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
MONITORED_MINT = os.getenv("MONITORED_MINT")

# Adrese top holdera direktno u kodu
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "6eT6tdrCxK... (dodaj ostale adrese ovde)"
]

DEX_PAIR_ID = "AyCkqVa1iJtXndu2KQSTSC3WQb3KP1H96tSG26CUaCKn"


def fetch_holder_transactions(start_time, end_time):
    all_transactions = []
    most_active = None
    max_volume = 0

    for rank, address in enumerate(HOLDER_LIST, start=1):
        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
        except Exception as e:
            print(f"[Fetch Error] {e}")
            continue

        for tx in data:
            ts = tx.get("timestamp")
            if not isinstance(ts, int):
                continue
            dt = datetime.utcfromtimestamp(ts)
            if not (start_time <= dt <= end_time):
                continue

            for transfer in tx.get("tokenTransfers", []):
                if transfer.get("mint") == MONITORED_MINT:
                    action = "buy" if transfer["toUserAccount"] == address else "sell"
                    amount = float(transfer["tokenAmount"]["uiAmount"])
                    tx_data = {
                        "address": address,
                        "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                        "action": action,
                        "rank": rank
                    }
                    all_transactions.append(tx_data)

                    if amount > max_volume:
                        max_volume = amount
                        most_active = tx_data

    return all_transactions, most_active


def get_token_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR_ID}"
        response = requests.get(url)
        data = response.json()
        return float(data["pair"]["priceUsd"])
    except Exception as e:
        print(f"[Price Error] {e}")
        return 0.0


def fetch_global_volume(start_time, end_time):
    all_transactions, _ = fetch_holder_transactions(start_time, end_time)
    buy = sum(tx["amount"] for tx in all_transactions if tx["action"] == "buy")
    sell = sum(tx["amount"] for tx in all_transactions if tx["action"] == "sell")
    return {"buy": buy * get_token_price(), "sell": sell * get_token_price()}


def send_telegram_message(bot, chat_id, text):
    asyncio.run(bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown"))





