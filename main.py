from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import os
import asyncio

from utils import (
    fetch_holder_transactions,
    get_token_price,
    fetch_global_volume,
    send_telegram_message,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = await fetch_holder_transactions(start_time, end_time)
        token_price = await get_token_price()
        total_volume = await fetch_global_volume(start_time, end_time)

        message_lines = [
            f"📈 *Izveštaj za poslednjih 1h*",
            f"💰 Cena tokena: ${token_price:.6f}" if token_price else "💰 Cena tokena: Nepoznata",
            f"🔄 Ukupno kupljeno: ${total_volume['buy']:.2f}" if total_volume else "🔄 Ukupno kupljeno: Nepoznato",
            f"🔻 Ukupno prodato: ${total_volume['sell']:.2f}" if total_volume else "🔻 Ukupno prodato: Nepoznato",
        ]

        if holder_data:
            message_lines.append("👥 Aktivnosti top holdera:\n")
            for holder in holder_data:
                addr_link = f"[{holder['address']}](https://solscan.io/account/{holder['address']})"
                action = "kupio" if holder["action"] == "buy" else "prodao" if holder["action"] == "sell" else "primio"
                message_lines.append(
                    f"🔹 Holder #{holder['rank']} {addr_link} je {action} {holder['amount']} tokena u {holder['timestamp']}."
                )
        else:
            message_lines.append("⚠️ Nema aktivnosti holdera u poslednjih 1h.")

        await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        print(f"[Greška u izveštaju] {e}")

@scheduler.scheduled_job("interval", hours=1)
def scheduled_task():
    asyncio.run(generate_report())

if __name__ == "__main__":
    asyncio.run(generate_report())  # Run once on startup
    scheduler.start()









