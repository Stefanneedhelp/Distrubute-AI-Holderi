import httpx
import os
from datetime import datetime
import logging

DEXSCANNER_TOKEN = os.getenv("DEXSCANNER_TOKEN")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

HOLDERS = [
    {"rank": 1, "address": "7bQ6uYkwKCEfVZ6MifMZzQWd3hp19uUjnZb9HfaQRpVQ"},
    {"rank": 2, "address": "JD25qVdtd65FoiXNmR89JjmoJdYk9sjYQeSTZAALFiMy"},
    {"rank": 3, "address": "8LVpipb9bq9qPfZTsay7ZwneW7nr6bGvdJyqwTA6G6d2"},
    {"rank": 4, "address": "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"}
]

TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"

async def fetch_holder_transactions(start_time, end_time):
    base_url = f"https://api.helius.xyz/v0/addresses"
    headers = {"accept": "application/json"}
    results = []

    for holder in HOLDERS:
        url = f"{base_url}/{holder['address']}/transactions?api-key={HELIUS_API_KEY}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                for tx in data:
                    ts = tx.get("timestamp")
                    if not ts:
                        continue
                    timestamp = datetime.utcfromtimestamp(ts)
                    if not (start_time <= timestamp <= end_time):
                        continue

                    for transfer in tx.get("tokenTransfers", []):
                        if transfer["mint"] != TOKEN_MINT:
                            continue

                        amount = float(transfer.get("tokenAmount", {}).get("uiAmountString", 0))
                        source = transfer.get("fromUserAccount")
                        destination = transfer.get("toUserAccount")

                        action = "transfer"
                        if source == holder["address"]:
                            action = "sell"
                        elif destination == holder["address"]:
                            action = "buy"

                        results.append({
                            "rank": holder["rank"],
                            "address": holder["address"],
                            "amount": amount,
                            "timestamp": timestamp.strftime("%H:%M"),
                            "action": action
                        })
        except Exception as e:
            logging.warning(f"[Fetch Error] Holder {holder['rank']} – {e}")

    return results

async def get_token_price():
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{TOKEN_MINT}"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            return float(r.json()["pair"]["priceUsd"])
    except Exception as e:
        logging.warning(f"[Price Error] {e}")
        return 0.0

async def fetch_global_volume(start_time, end_time):
    base_url = f"https://api.helius.xyz/v0/token/{TOKEN_MINT}/transfers?api-key={HELIUS_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(base_url)
            r.raise_for_status()
            data = r.json()

            total_buy = 0
            total_sell = 0

            for tx in data:
                ts = tx.get("timestamp")
                if not ts:
                    continue
                timestamp = datetime.utcfromtimestamp(ts)
                if not (start_time <= timestamp <= end_time):
                    continue
                amount = float(tx.get("tokenAmount", {}).get("uiAmountString", 0))
                if tx.get("type") == "TRANSFER" and tx.get("source") == "UNKNOWN":
                    continue

                if tx.get("fromUserAccount") in [h["address"] for h in HOLDERS]:
                    total_sell += amount * await get_token_price()
                elif tx.get("toUserAccount") in [h["address"] for h in HOLDERS]:
                    total_buy += amount * await get_token_price()

            return {"buy": total_buy, "sell": total_sell}
    except Exception as e:
        logging.warning(f"[Volume Error] {e}")
        return {"buy": 0, "sell": 0}

async def send_telegram_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.warning(f"[Telegram Error] {e}")


