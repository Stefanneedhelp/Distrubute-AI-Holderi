
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
MONITORED_MINT = os.getenv("MONITORED_MINT")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

bot = Bot(token=TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Paris")

# Funkcija za izveštaj
@scheduler.scheduled_job("cron", hour=6, minute=0)
def generate_report():
    try:
        end_time = datetime.now(pytz.utc)
        start_time = end_time - timedelta(hours=1)

        holders_data, most_active_holder, buy_total, sell_total = fetch_holder_transactions(
            HELIUS_API_KEY, MONITORED_MINT, start_time, end_time
        )

        token_price = get_token_price()
        ratio = round(buy_total / sell_total, 2) if sell_total > 0 else "∞"

        message_lines = [
            f"📊 <b>Dnevni izveštaj</b> ({end_time.strftime('%Y-%m-%d %H:%M')})",
            f"<b>Cena:</b> ${token_price:.6f}",
            f"<b>Ukupno kupljeno:</b> ${buy_total:,.2f}",
            f"<b>Ukupno prodato:</b> ${sell_total:,.2f}",
            f"<b>Odnos kupovina/prodaja:</b> {ratio}"
        ]

        if holders_data:
            message_lines.append("\n<b>📢 Aktivnosti top holdera:</b>")
            for h in holders_data:
                action_text = "kupio" if h["type"] == "BUY" else "prodao" if h["type"] == "SELL" else "primio"
                message_lines.append(
                    f"👤 Holder #{h['rank']} <a href='https://solscan.io/account/{h['address']}'>...{h['address'][-4:]}</a> je {action_text} {h['amount']:.2f} tokena u {h['timestamp']}"
                )
        else:
            message_lines.append("\n📬 <b>Nema aktivnosti holdera</b>")

        if most_active_holder:
            message_lines.append(f"\n🔍 Najaktivniji holder: <a href='https://solscan.io/account/{most_active_holder[0]}'>...{most_active_holder[0][-4:]}</a> sa {most_active_holder[1]} transakcija")

        send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        logging.error(f"[Greška u izveštaju] {e}")

if __name__ == "__main__":
    scheduler.start()





