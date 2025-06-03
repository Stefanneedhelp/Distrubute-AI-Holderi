import asyncio
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import pytz
import os
import logging

from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message

# Konfiguracija logovanja
logging.basicConfig(level=logging.INFO)

# Učitavanje varijabli iz okruženja
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

# Scheduler za slanje izveštaja
scheduler = AsyncIOScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = await fetch_holder_transactions(start_time, end_time)
        token_price = await get_token_price()
        total_volume = await fetch_global_volume(start_time, end_time)

        message_lines = [
            f"📊 *1h izveštaj za token*",
            f"💰 Cena: ${token_price:.6f}",
            f"🟢 Kupovine: ${total_volume['buy']:.2f}",
            f"🔴 Prodaje: ${total_volume['sell']:.2f}",
        ]

        if holder_data:
            message_lines.append("\n👑 Aktivnosti top holdera:")
            for h in holder_data:
                action = "kupio" if h["action"] == "buy" else "prodao" if h["action"] == "sell" else "primio"
                message_lines.append(
                    f"• Holder #{h['rank']} ([{h['address']}](https://solscan.io/account/{h['address']})) je {action} {h['amount']} tokena u {h['timestamp']}"
                )
        else:
            message_lines.append("⚠️ Nema aktivnosti holdera u prethodnih 1h.")

        await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        logging.error(f"[Greška u izveštaju] {e}")

# Dodaj job na svakih 1 sat
scheduler.add_job(generate_report, 'interval', hours=1)

if __name__ == "__main__":
    scheduler.start()
    asyncio.get_event_loop().run_forever()






