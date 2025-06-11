import os
import requests
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
DIS_MINT = os.getenv("DIS_MINT")

async def get_token_price():
    try:
        url = f"https://public-api.birdeye.so/public/price?address={DIS_MINT}"
        headers = {
            "accept": "application/json",
            "X-API-KEY": BIRDEYE_API_KEY
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return data["data"]["value"]
    except Exception as e:
        print("[ERROR get_token_price]", e)
        return 0.0

async def send_telegram_message(message):
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print("[ERROR send_telegram_message]", e)
