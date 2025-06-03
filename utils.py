import os
import httpx
import logging
from datetime import datetime
from holders import HOLDERS
from telegram import Bot
from dateutil import parser as date_parser

API_KEY = os.getenv("HELIUS_API_KEY")
TOKEN_ADDRESS = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
DEX_PAIR_ID = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"

logging.basicConfig(level=logging.INFO)

async def fetch_holder_transactions(start_time, end_time):
    transactions = []
    headers = {"accept": "application/json"}

    async with httpx.AsyncClient() as client:
        for rank, address in enumerate(HOLDERS, 1):
            try:
                url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={API_KEY}"
                res = await client.get(url, headers=headers)
                data = res.json()

                for tx in data:
                    timestamp = tx.get("timestamp")
                    if isinstance(timestamp, int):
                        tx_time = datetime.utcfromtimestamp(timestamp)
                    else:
                        tx_time = date_parser.parse(str(timestamp))

                    if not (start_time <= tx_time <= end_time):
                        continue

                    for token_event in tx.get("tokenTransfers", []):
                        if token_event.get("mint") == TOKEN_ADDRESS:
                            action = (
                                "buy" if token_event["toUserAccount"] == address else
                                "sell" if token_event["fromUserAccount"] == address else
                                "receive"
                            )
                            transactions.append({
                                "rank": rank,
                                "address": address,
                                "amount": float(token_event.get("tokenAmount", {}).get("uiAmount", 0)),
                                "timestamp": tx_time.strftime("%H:%M:%S"),
                                "action": action,
                            })

            except Exception as e:
                logging.warning(f"[Fetch Error] Holder {rank} – {e}")
    return transactions

async def get_token_price():
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR_ID}"
            res = await client.get(url)
            data = res.json()
            return float(data["pair"]["priceUsd"])
    except Exception as e:
        logging.warning(f"[Price Error] {e}")
        return None

async def fetch_global_volume(start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/token/{TOKEN_ADDRESS}/transfers?api-key={API_KEY}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            data = res.json()

        volume = {"buy": 0, "sell": 0}
        for tx in data:
            timestamp = tx.get("timestamp")
            if isinstance(timestamp, int):
                tx_time = datetime.utcfromtimestamp(timestamp)
            else:
                tx_time = date_parser.parse(str(timestamp))

            if not (start_time <= tx_time <= end_time):
                continue

            direction = "buy" if tx["toUserAccount"] in HOLDERS else "sell" if tx["fromUserAccount"] in HOLDERS else None
            amount = float(tx.get("tokenAmount", {}).get("uiAmount", 0))
            if direction in volume:
                volume[direction] += amount * (await get_token_price() or 0)

        return volume
    except Exception as e:
        logging.warning(f"[Volume Error] {e}")
        return None

async def send_telegram_message(bot: Bot, chat_id: str, text: str):
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")




