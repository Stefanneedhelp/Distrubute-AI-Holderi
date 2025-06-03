import requests
from datetime import datetime
import pytz
import os
from telegram import Bot

# 🔧 Postavi API ključ iz Render environment-a
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
DEX_PAIR_ID = os.getenv("DEX_PAIR_ID")
bot = Bot(token=os.getenv("BOT_TOKEN"))

# ✅ Direktno ubačene adrese holdera
HOLDER_LIST = [
    "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ",
    "E5WchutHdCY8besK1gFg8Bc5AzXssZeDPKrNGWWemiiP",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF"
]

def send_telegram_message(bot, chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"[Send Error] {e}")

def fetch_holder_transactions(start_time, end_time):
    results = []
    for rank, address in enumerate(HOLDER_LIST, start=1):
        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}&limit=100"
        try:
            response = requests.get(url)
            data = response.json()

            for tx in data:
                ts = tx.get("timestamp")
                if not isinstance(ts, int):
                    continue
                dt = datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc)
                if not (start_time <= dt <= end_time):
                    continue

                for transfer in tx.get("tokenTransfers", []):
                    mint = transfer.get("mint")
                    action = transfer.get("tokenStandard", "").lower()
                    sender = transfer.get("fromUserAccount")
                    receiver = transfer.get("toUserAccount")
                    amount = transfer.get("tokenAmount", {}).get("uiAmountString", "0")

                    holder_action = "receive"
                    if receiver == address:
                        holder_action = "buy"
                    elif sender == address:
                        holder_action = "sell"

                    results.append({
                        "rank": rank,
                        "address": address,
                        "action": holder_action,
                        "amount": amount,
                        "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    })
        except Exception as e:
            print(f"[Fetch Error] {e}")
    return results

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
    try:
        url = f"https://api.helius.xyz/v0/token-transfers?api-key={HELIUS_API_KEY}"
        # Nema filters, pa se samo vraća dummy vrednost za sada
        return {"buy": 0, "sell": 0}
    except Exception as e:
        print(f"[Volume Error] {e}")
        return {"buy": 0, "sell": 0}
