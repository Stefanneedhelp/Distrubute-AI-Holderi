
from telegram import Bot 
from apscheduler.schedulers.blocking import BlockingScheduler 
from datetime import datetime, timedelta 
from dotenv import load_dotenv 
import pytz 
import os

from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN") 
CHAT_ID = os.getenv("CHAT_ID") 
bot = Bot(token=TOKEN) scheduler = BlockingScheduler(timezone="Europe/Paris")

def generate_report(): try: end_time = datetime.now(pytz.utc) start_time = end_time - timedelta(hours=1)

holder_data = fetch_holder_transactions(start_time, end_time)
    token_price = get_token_price()
    total_volume = fetch_global_volume(start_time, end_time)

    message_lines = [
        f"📈 *Izveštaj za poslednjih 1h*",
        f"💰 Cena tokena: ${token_price:.6f}",
        f"🔄 Ukupno kupljeno: ${total_volume['buy']:.2f}",
        f"🔻 Ukupno prodato: ${total_volume['sell']:.2f}"
    ]

    if holder_data:
        message_lines.append(f"�




