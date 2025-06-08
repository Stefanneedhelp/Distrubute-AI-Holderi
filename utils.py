from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
import pytz
import os
import asyncio
import time

from utils import get_token_price, fetch_global_volume_delta, send_telegram_message

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
scheduler = BlockingScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        async with Bot(token=TOKEN) as bot:
            token_price = await get_token_price()
            total_volume = await fetch_global_volume_delta()

            print("[DEBUG] Cena:", token_price)
            print("[DEBUG] Volumen:", total_volume)

            message_lines = [
                "📈 <b>Izveštaj za poslednjih 15 minuta</b>",
                f"💰 Cena tokena: ${token_price:.6f}" if token_price else "💰 Cena tokena: Nepoznata",
            ]

            if total_volume and "buy" in total_volume and "sell" in total_volume:
                message_lines.append(f"🟢 Ukupno kupljeno: ${total_volume['buy']:.2f}")
                message_lines.append(f"🔴 Ukupno prodato: ${total_volume['sell']:.2f}")
            else:
                message_lines.append("🟢 Ukupno kupljeno: Nepoznato")
                message_lines.append("🔴 Ukupno prodato: Nepoznato")

            await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        print(f"[Greška u izveštaju] {e}")

# ⏱ Na svakih 15 minuta
@scheduler.scheduled_job("interval", minutes=15)
def scheduled_task():
    asyncio.run(generate_report())

if __name__ == "__main__":
    asyncio.run(generate_report())  # Odmah po pokretanju
    scheduler.start()

    while True:
        time.sleep(60)


