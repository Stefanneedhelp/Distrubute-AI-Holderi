from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from telegram import Bot
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
            price, buy_volumes, sell_volumes = await fetch_dexscreener_data()

            message_lines = [
                f"📈 <b>Izveštaj za DIS token</b>",
                f"💰 Cena: ${price:.6f}",
                "",
                f"🟢 <b>Kupovine</b>:",
                f"• 5 min: ${buy_volumes.get('m5', 0):,.2f}",
                f"• 1h: ${buy_volumes.get('h1', 0):,.2f}",
                f"• 6h: ${buy_volumes.get('h6', 0):,.2f}",
                f"• 24h: ${buy_volumes.get('h24', 0):,.2f}",
                "",
                f"🔴 <b>Prodaje</b>:",
                f"• 5 min: ${sell_volumes.get('m5', 0):,.2f}",
                f"• 1h: ${sell_volumes.get('h1', 0):,.2f}",
                f"• 6h: ${sell_volumes.get('h6', 0):,.2f}",
                f"• 24h: ${sell_volumes.get('h24', 0):,.2f}",
            ]

            await bot.send_message(chat_id=CHAT_ID, text="\n".join(message_lines), parse_mode="HTML")
    except Exception as e:
        print(f"[Bot error] {e}")

@scheduler.scheduled_job('interval', minutes=5)
def scheduled_job():
    asyncio.run(generate_report())

if __name__ == "__main__":
    scheduler.start()





