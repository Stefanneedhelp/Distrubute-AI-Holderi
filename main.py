from telegram import Bot from apscheduler.schedulers.blocking import BlockingScheduler from datetime import datetime, timedelta from dotenv import load_dotenv import pytz import os

from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN") CHAT_ID = os.getenv("CHAT_ID") bot = Bot(token=TOKEN) scheduler = BlockingScheduler(timezone="Europe/Paris")

def generate_report(): try: end_time = datetime.now(pytz.utc) start_time = end_time - timedelta(hours=1)

holder_data = fetch_holder_transactions(start_time, end_time)
    token_price = get_token_price()
    total_volume = fetch_global_volume(start_time, end_time)

    delta_volume = total_volume['buy'] - total_volume['sell']

    message_lines = [
        f"\U0001F4C8 *Izveštaj za poslednjih 1h*",
        f"\U0001F4B0 Cena tokena: ${token_price:.6f}",
        f"\U0001F501 Ukupno kupljeno: ${total_volume['buy']:.2f}",
        f"\U0001F53B Ukupno prodato: ${total_volume['sell']:.2f}",
        f"\U0001F4CA Razlika (kupovina - prodaja): ${delta_volume:.2f}"
    ]

    if holder_data:
        most_active_holder = max(holder_data, key=lambda h: h.get('usd_volume', 0))
        most_active_address = most_active_holder['address']
        message_lines.append(f"\U0001F465 Najaktivniji holder: [{most_active_address}](https://solscan.io/account/{most_active_address})\n")

        message_lines.append(f"\U0001F465 Aktivnosti top holdera:")
        for holder in holder_data:
            addr_link = f"[{holder['address']}](https://solscan.io/account/{holder['address']})"
            action = "kupio" if holder["action"] == "buy" else "prodao" if holder["action"] == "sell" else "primio"
            message_lines.append(
                f"\u2729 Holder #{holder['rank']} {addr_link} je {action} {holder['amount']} tokena u {holder['timestamp']}."
            )
    else:
        message_lines.append("\u26A0\uFE0F Nema aktivnosti holdera u poslednjih 1h.")

    message = "\n".join(message_lines)
    send_telegram_message(bot, CHAT_ID, message)

except Exception as e:
    print(f"[Greška u izveštaju] {e}")

Zakazivanje izveštaja svakih 1 sat

scheduler.add_job(generate_report, 'interval', hours=1)

if name == "main": scheduler.start()






