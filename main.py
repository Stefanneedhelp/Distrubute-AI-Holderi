import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message

load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")
TOKEN = os.getenv("BOT_TOKEN")
HOLDER_ADDRESSES = os.getenv("HOLDER_ADDRESSES", "[]")

scheduler = BlockingScheduler()

@scheduler.scheduled_job("cron", hour=6, minute=0)
def generate_report():
    try:
        now = datetime.utcnow()
        start_time = now - timedelta(days=1)
        end_time = now

        print("🕕 Vremenski okvir:", start_time, "-", end_time)

        # Cena tokena
        price = get_token_price()

        # Aktivnosti holdera
        activities, holders_with_activity = fetch_holder_transactions(start_time, end_time)

        # Ukupni volumen
        volume_summary = fetch_global_volume(start_time, end_time)

        if not holders_with_activity:
            message = f"📈 *Dnevni izveštaj*

💰 Cena tokena: ${price}

📊 Aktivnosti holdera:
Nema aktivnosti holdera u poslednja 24h."
        else:
            message = f"📈 *Dnevni izveštaj*

💰 Cena tokena: ${price}

📊 Aktivnosti holdera:
"
            for entry in activities:
                message += entry + "\n"

        message += f"\n📉 Ukupan volumen:
{volume_summary}"

        send_telegram_message(message)

    except Exception as e:
        print("[Greška u izveštaju]", e)


if __name__ == "__main__":
    print("📡 Bot pokrenut. Čeka vreme za izveštaj...")
    scheduler.start()






