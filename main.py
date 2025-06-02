
import os
import pytz
import logging
from dotenv import load_dotenv
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

from utils import (
    fetch_holder_transactions,
    get_token_price,
    fetch_global_volume,
    send_telegram_message
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TOP_HOLDERS = os.getenv("TOP_HOLDERS", "").split(",")

bot = Bot(token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=24)

        transactions = fetch_holder_transactions(start_time, end_time, TOP_HOLDERS)
        price = get_token_price()
        global_volume = fetch_global_volume(start_time, end_time)

        message_lines = [f"📈 *Dnevni izveštaj*\n\n💰 Cena tokena: ${price:.6f}"]

        if transactions:
            message_lines.append("\n🧾 Aktivnosti holdera:")
            for tx in transactions:
                holder_number = tx.get("rank", "?")
                address = tx["address"]
                action = tx["action"]
                amount = tx["amount"]
                counterparty = tx.get("counterparty", "Nepoznato")
                tx_time = tx.get("timestamp", "Nepoznato")
                link = f"https://solscan.io/account/{address}"

                message_lines.append(
                    f"[{holder_number}. Holder]({link}) je *{action}* {amount:.2f} tokena sa {counterparty} u {tx_time}"
                )
        else:
            message_lines.append("\n📭 Nema aktivnosti holdera u poslednja 24h.")

        if global_volume:
            message_lines.append(f"\n📊 Ukupan promet:\n- Kupovine: ${global_volume['buy']:.2f}\n- Prodaje: ${global_volume['sell']:.2f}")
        else:
            message_lines.append("\n⚠️ Nema globalnog volumena.")

        send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        logging.error(f"[Greška u izveštaju] {e}")

# Zakazivanje
scheduler = BlockingScheduler(timezone='Europe/Paris')

# Svaki dan u 6:00
scheduler.add_job(generate_report, CronTrigger(hour=6, minute=0))

# TEMP: pokreći svakih 60 minuta (za testiranje — ukloni kad prebaciš na samo 6h)
# from apscheduler.triggers.interval import IntervalTrigger
# scheduler.add_job(generate_report, IntervalTrigger(minutes=60))

generate_report()  # Pozovi odmah pri startovanju (testiranje)
scheduler.start()





