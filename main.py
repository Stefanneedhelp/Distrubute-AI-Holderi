from telegram import Bot
from utils import fetch_holder_transactions, get_token_price, fetch_global_volume
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(BOT_TOKEN)
scheduler = BlockingScheduler(timezone=pytz.timezone("Europe/Paris"))

@scheduler.scheduled_job("cron", hour=6, minute=0)
def generate_report():
    now = datetime.utcnow()
    start_time = now - timedelta(days=1)
    end_time = now

    price = get_token_price()
    holder_data = fetch_holder_transactions(start_time, end_time)
    global_volume = fetch_global_volume(start_time, end_time)

    if not holder_data:
        message = f"""📈 *Dnevni izveštaj*

🕕 Period: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}
💰 Cena tokena: ${price}

📊 Aktivnosti holdera:
Nema aktivnosti holdera u poslednja 24h."""
    else:
        message = f"""📈 *Dnevni izveštaj*

🕕 Period: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}
💰 Cena tokena: ${price}

📊 Aktivnosti holdera:"""
        for idx, h in enumerate(holder_data, 1):
            direction = "prodao" if h["amount_usd"] < 0 else "kupio"
            message += f"""

{idx}. [📟 {h['address']}](https://solscan.io/account/{h['address']})
🔁 {direction} {abs(h['amount_token']):,.2f} tokena (~${abs(h['amount_usd']):,.2f})"""

    message += f"""

🌐 Ukupan volumen:
Kupovine: ${global_volume['buy']:,}
Prodaje: ${global_volume['sell']:,}"""

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

if __name__ == "__main__":
    scheduler.start()







