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
bot = Bot(token=TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Paris")

# Glavna funkcija izveštaja
def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holder_data = fetch_holder_transactions(start_time, end_time)
        token_price = get_token_price()
        total_volume = fetch_global_volume(start_time, end_time)

        message_lines = [
            "📈 *Izveštaj za poslednjih 1h*",
            f"💰 Cena tokena: ${token_price:.6f}",
            f"🔄 Ukupno kupljeno: ${total_volume['buy']:.2f}",
            f"🔻 Ukupno prodato: ${total_volume['sell']:.2f}"
        ]

        if holder_data:
            message_lines.append("👥 Aktivnosti top holdera:\n")

            # Pronađi najaktivnijeg
            activity_counts = {}
            for holder in holder_data:
                key = holder["address"]
                activity_counts[key] = activity_counts.get(key, 0) + 1

            most_active = max(activity_counts.items(), key=lambda x: x[1])
            message_lines.append(f"🔥 Najaktivniji holder: [{most_active[0]}](https://solscan.io/account/{most_active[0]}) ({most_active[1]} transakcija)\n")

            for holder in holder_data:
                addr_link = f"[{holder['address']}](https://solscan.io/account/{holder['address']})"
                action = "kupio" if holder["action"] == "buy" else "prodao" if holder["action"] == "sell" else "primio"
                message_lines.append(
                    f"🔹 Holder #{holder['rank']} {addr_link} je {action} {holder['amount']} tokena u {holder['timestamp']}."
                )
        else:
            message_lines.append("📭 Nema aktivnosti holdera u poslednjih 1h.")

        message = "\n".join(message_lines)
        send_telegram_message(bot, CHAT_ID, message)

    except Exception as e:
        logging.error(f"[Greška u izveštaju] {e}")

# Zakazivanje izveštaja na 1 sat
scheduler.add_job(generate_report, 'interval', hours=1)

if __name__ == "__main__":
    scheduler.start()




