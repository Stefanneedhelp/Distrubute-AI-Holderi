from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
import pytz
import os
import asyncio

from utils import fetch_dexscreener_data

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
scheduler = BlockingScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        async with Bot(token=TOKEN) as bot:
            price, buy_volume, sell_volume = await fetch_dexscreener_data()

            message_lines = [
                f"📈 <b>Izveštaj za poslednjih 15 minuta</b>",
                f"💰 Cena tokena: ${price:.6f}",
                f"🟢 Ukupno kupljeno: ${buy_volume:,.2f}",
                f"🔴 Ukupno prodato: ${sell_volume:,.2f}"
            ]

            await bot.send_message(chat_id=CHAT_ID, text="\n".join(message_lines), parse_mode="HTML")
    except Exception as e:
        print(f"[Bot error] {e}")

@scheduler.scheduled_job('interval', minutes=15)
def scheduled_job():
    asyncio.run(generate_report())

if __name__ == "__main__":
    scheduler.start()







