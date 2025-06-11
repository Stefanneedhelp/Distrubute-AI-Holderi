import os
import requests
from telegram import Bot

# ✅ Dobavljanje cene DIS tokena preko BirdEye API-ja
async def get_token_price():
    try:
        api_key = os.getenv("BIRDEYE_API_KEY")
        dis_mint = os.getenv("DIS_MINT")

        url = f"https://public-api.birdeye.so/public/price?address={dis_mint}"
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }

        res = requests.get(url, headers=headers)
        data = res.json()

        price = data.get("data", {}).get("value", 0.0)
        return price

    except Exception as e:
        print("[ERROR get_token_price]", e)
        return 0.0

# ✅ Slanje poruke na Telegram
async def send_telegram_message(message):
    try:
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("CHAT_ID")

        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print("[ERROR send_telegram_message]", e)
