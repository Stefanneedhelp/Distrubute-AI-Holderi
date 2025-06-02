
import os
import requests
from datetime import datetime
import pytz

HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF",
    "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy",
    "6FBfpptRGqrqqxiFrAGZavJp8Z9GXF2MAC8zWARZpF1f",
    "mpTFvuadXpvu48KUsWv4oNcBXMrk6nVLKDzsA8i8kKQ",
    "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2",
    "7MV6vtiFJPhHgBQc6Ch4hHCrYfXRr5xkbqEVUnomKXCK",
    "CniPCE4b3s8gSUPhUiyMjXnytrEqUrMfSsnbBjLCpump",
    "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf",
    "GtiwjVEQwbaXVkDn7EGteqHwT1KNVxD5XhKMzfgaEKuw",
    "E5WchutHdCY8besK1gFg8Bc5AzXssZeDPKrNGWWemiiP",
    "5q3Pv9GY57qUakaUNSLT8n28h3UKwUS8Dcy8f4GzT7k2"
]

def fetch_holder_transactions(start_time, end_time):
    url = os.getenv("HELIUS_URL")
    headers = {"Content-Type": "application/json"}

    results = []

    for rank, address in enumerate(HOLDER_LIST, 1):
        body = {
            "account": address,
            "limit": 100,
            "before": None,
            "until": None
        }
        try:
            response = requests.post(f"{url}/v0/addresses/{address}/transactions", json=body, headers=headers)
            txs = response.json()

            for tx in txs:
                timestamp = datetime.fromtimestamp(tx["timestamp"], tz=pytz.utc)
                if not (start_time <= timestamp <= end_time):
                    continue

                for transfer in tx.get("tokenTransfers", []):
                    if transfer.get("mint") != os.getenv("MONITORED_MINT"):
                        continue

                    if transfer.get("toUserAccount") == address:
                        action = "buy"
                    elif transfer.get("fromUserAccount") == address:
                        action = "sell"
                    else:
                        action = "other"

                    results.append({
                        "rank": rank,
                        "address": address,
                        "amount": round(float(transfer.get("tokenAmount", {}).get("userAmount", 0)), 2),
                        "action": action,
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    })
        except Exception as e:
            print(f"[Fetch Error] {e}")

    return results

def get_token_price():
    try:
        url = os.getenv("DEXSCREENER_URL")
        response = requests.get(url)
        data = response.json()
        return float(data["pairs"][0]["priceUsd"])
    except Exception as e:
        print(f"[Price Error] {e}")
        return 0.0

def fetch_global_volume(start_time, end_time):
    url = os.getenv("HELIUS_URL")
    mint = os.getenv("MONITORED_MINT")
    headers = {"Content-Type": "application/json"}

    body = {
        "query": {
            "mint": mint,
            "rawTransaction": True
        },
        "limit": 1000
    }

    try:
        response = requests.post(f"{url}/v1/transactions", json=body, headers=headers)
        txs = response.json()

        buy_total = 0.0
        sell_total = 0.0
        holder_activity = {}

        for tx in txs:
            timestamp = datetime.fromtimestamp(tx["timestamp"], tz=pytz.utc)
            if not (start_time <= timestamp <= end_time):
                continue

            for transfer in tx.get("tokenTransfers", []):
                if transfer.get("mint") != mint:
                    continue

                amount = round(float(transfer.get("tokenAmount", {}).get("userAmount", 0)), 2)

                if transfer.get("toUserAccount") in HOLDER_LIST:
                    buy_total += amount * get_token_price()
                    addr = transfer["toUserAccount"]
                    holder_activity[addr] = holder_activity.get(addr, 0) + amount
                elif transfer.get("fromUserAccount") in HOLDER_LIST:
                    sell_total += amount * get_token_price()
                    addr = transfer["fromUserAccount"]
                    holder_activity[addr] = holder_activity.get(addr, 0) + amount

        most_active = max(holder_activity.items(), key=lambda x: x[1])[0] if holder_activity else None
        return {"buy": buy_total, "sell": sell_total, "most_active": most_active}

    except Exception as e:
        print(f"[Global Volume Error] {e}")
        return {"buy": 0.0, "sell": 0.0, "most_active": None}

def send_telegram_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        print(f"[Telegram Error] {e}")






