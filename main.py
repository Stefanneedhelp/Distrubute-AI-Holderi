
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from telegram import Bot
import os
import asyncio

from utils import fetch_dexscreener_data, get_dexscreener_link

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
scheduler = BlockingScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        async with Bot(token=TOKEN) as bot:
            price, buy_24h, sell_24h = await fetch_dexscreener_data()
            dexscreener_link = get_dexscreener_link()

            message_lines = [
                f"📈 <b>Izveštaj za DIS token (24h)</b>",
                f"💰 Cena: ${price:.6f}",
                "",
                f"🟢 <b>Kupovine (24h)</b>: ${buy_24h:,.2f}",
                f"🔴 <b>Prodaje (24h)</b>: ${sell_24h:,.2f}",
                "",
                f"🏃‍♂️ <b>Najaktivnija adresa:</b> (uskoro)",
                "",
                f"📊 <a href=\"{dexscreener_link}\">Dexscreener DIS/SOL</a>"
            ]

            await bot.send_message(chat_id=CHAT_ID, text="\n".join(message_lines), parse_mode="HTML")
    except Exception as e:
        print(f"[Bot error] {e}")

@scheduler.scheduled_job('interval', minutes=5)
def scheduled_job():
    asyncio.run(generate_report())

if __name__ == "__main__":
    scheduler.start()



