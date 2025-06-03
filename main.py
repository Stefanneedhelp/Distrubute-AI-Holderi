from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import os
import logging

from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message

# Učitaj .env promenljive
load_dotenv()

# Konfiguracija
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
MONITORED_MINT = os.getenv("MONITORED_MINT")

bot = Bot(token=TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Paris")

def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = fetch_holder_transactions(HELIUS_API_KEY, MONITORED_MINT, start_time, end_time)
        token_price = get_token_price(MONITORED_MINT)
        total_volume = fetch_global_volume(MONITORED_MINT, HELIUS_API_KEY, start_time, end_time)

        message_lines = [
            f"📈 <b>Dnevni izveštaj</b> ({end_time.strftime('%Y-%m-%d %H:%M')})",
            f"<b>Cena:</b> ${token_price:.6f}",
            f"<b>Ukupno kupljeno:</b> ${total_volume['buy']:.2f}",
            f"<b>Ukupno prodato:</b> ${total_volume['sell']:.2f}",
            f"<b>Odnos kupovina/prodaja:</b> {(total_volume['buy'] / total_volume['sell'] if total_volume['sell'] else 0):.2f}",
        ]

        if holder_data:
            most_active = max(holder_data, key=lambda x: x["tx_count"])
            message_lines.append(
                f"\n🔥 Najaktivniji holder: <a href='https://solscan.io/account/{most_active['address']}'>{most_active['address']}</a> "
                f"({most_active['tx_count']} transakcija)"
            )
        else:
            message_lines.append("📭 <b>Nema aktivnosti holdera</b>")

        message = "\n".join(message_lines)
        send_telegram_message(bot, CHAT_ID, message)

    except Exception as e:
        logging.error(f"[Greška u izveštaju] {e}")

# Zakazivanje izveštaja svakih 1h (promeni u hours=6 za 6h)
scheduler.add_job(generate_report, 'interval', hours=1)

if __name__ == "__main__":
    scheduler.start()



