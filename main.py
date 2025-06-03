from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import os
import logging

from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message

load_dotenv()

# Konfiguracija
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Paris")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@scheduler.scheduled_job("interval", hours=1)
def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = fetch_holder_transactions(start_time, end_time)
        token_price = get_token_price()
        volume_data = fetch_global_volume(start_time, end_time)

        message_lines = [
            f"📈 *Izveštaj za poslednjih 1h* ({end_time.strftime('%Y-%m-%d %H:%M')})",
            f"💰 Cena: ${token_price:.6f}",
            f"🔄 Ukupno kupljeno: ${volume_data['buy']:.2f}",
            f"🔻 Ukupno prodato: ${volume_data['sell']:.2f}",
            f"⚖️ Odnos kupovina/prodaja: {(volume_data['buy'] / (volume_data['sell'] or 1)):.2f}",
        ]

        if holder_data:
            top_holder = max(holder_data, key=lambda x: x["amount"])
            addr_link = f"[{top_holder['address']}](https://solscan.io/account/{top_holder['address']})"
            message_lines.append(f"🔎 Najaktivniji holder: {addr_link} sa {top_holder['amount']} tokena")
        else:
            message_lines.append("📬 Nema aktivnosti holdera u poslednjih 1h.")

        send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        logger.error(f"[Greška u izveštaju] {e}")

if __name__ == "__main__":
    generate_report()
    scheduler.start()






