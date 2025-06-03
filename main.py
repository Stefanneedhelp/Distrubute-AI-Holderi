import asyncio
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import os
import logging

from utils import (
    fetch_holder_transactions,
    get_token_price,
    fetch_global_volume,
    send_telegram_message
)

# Učitaj .env promenljive ako koristiš lokalno (nije neophodno na Renderu ako koristiš dashboard)
load_dotenv()

# Telegram postavke
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Zona
TIMEZONE = pytz.timezone("Europe/Paris")

# Glavna funkcija za generisanje izveštaja
async def generate_report():
    try:
        end_time = datetime.now(TIMEZONE).astimezone(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = await fetch_holder_transactions(start_time, end_time)
        token_price = await get_token_price()
        total_volume = await fetch_global_volume(start_time, end_time)

        message_lines = [
            f"📈 *Izveštaj za poslednjih 1h*",
            f"💰 Cena tokena: ${token_price:.6f}",
            f"🟢 Ukupno kupljeno: ${total_volume['buy']:.2f}",
            f"🔴 Ukupno prodato: ${total_volume['sell']:.2f}",
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
        logger.error(f"[Greška u izveštaju] {e}")

# Glavna asinhrona petlja
async def main():
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(generate_report, 'interval', hours=1)
    scheduler.start()

    # Ručno pokretanje prve provere odmah
    await generate_report()

    # Ne izlazi iz programa
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())






