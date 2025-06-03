import os
import pytz
import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from dotenv import load_dotenv

from utils import (
    fetch_holder_transactions,
    get_token_price,
    fetch_global_volume,
    send_telegram_message
)

load_dotenv()

# Konfiguracija
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)
scheduler = AsyncIOScheduler(timezone="Europe/Paris")

# Glavna funkcija za generisanje izveštaja
async def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = await fetch_holder_transactions(start_time, end_time)
        token_price = get_token_price()
        total_volume = fetch_global_volume(start_time, end_time)

        message_lines = [
            f"📉 *Izveštaj za poslednjih 1h* ({end_time.strftime('%Y-%m-%d %H:%M')})",
            f"💰 Cena: ${token_price:.6f}",
            f"🔄 Ukupno kupljeno: ${total_volume['buy']:.2f}",
            f"🔻 Ukupno prodato: ${total_volume['sell']:.2f}",
            f"⚖️ Odnos kupovina/prodaja: {total_volume['ratio']:.2f}"
        ]

        if holder_data:
            message_lines.append("👥 Aktivnosti top holdera:")
            for holder in holder_data:
                addr_link = f"[{holder['address']}](https://solscan.io/account/{holder['address']})"
                action = "kupio" if holder["action"] == "buy" else "prodao" if holder["action"] == "sell" else "primio"
                message_lines.append(
                    f"🔹 Holder #{holder['rank']} {addr_link} je {action} {holder['amount']} tokena u {holder['timestamp']}."
                )
        else:
            message_lines.append("📭 Nema aktivnosti holdera u poslednjih 1h.")

        await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        logging.error(f"[Greška u izveštaju] {e}")

# Zakazivanje asinhronog posla
scheduler.add_job(generate_report, "interval", hours=1)

if __name__ == "__main__":
    scheduler.start()
    asyncio.run(generate_report())  # pokreće odmah na startu







