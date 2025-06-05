from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from dotenv import load_dotenv
import pytz
import os
import asyncio

from fetch_holder_transactions import fetch_holder_transactions
from utils import get_token_price, fetch_global_volume, send_telegram_message
from holders import TOP_HOLDERS

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)
scheduler = BlockingScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        token_price = await get_token_price()
        total_volume = await fetch_global_volume()
        message_lines = [
            f"📈 <b>Izveštaj za poslednjih 1h</b>",
            f"💰 Cena tokena: ${token_price:.6f}" if token_price else "💰 Cena tokena: Nepoznata",
            f"🟢 Ukupno kupljeno: ${total_volume['buy']:.2f}" if total_volume else "🟢 Ukupno kupljeno: Nepoznato",
            f"🔴 Ukupno prodato: ${total_volume['sell']:.2f}" if total_volume else "🔴 Ukupno prodato: Nepoznato",
        ]

        holder_data = []

        for rank, address in enumerate(TOP_HOLDERS, start=1):
            txs = await fetch_holder_transactions(address)
            for tx in txs:
                holder_data.append({
                    "rank": rank,
                    "address": address,
                    "amount": abs(tx["delta"]),
                    "action": tx["side"].lower(),
                    "timestamp": datetime.utcfromtimestamp(tx["blockTime"]).strftime("%H:%M:%S"),
                })
            await asyncio.sleep(0.3)

        if holder_data:
            message_lines.append("\n👥 <b>Aktivnosti top holdera:</b>\n")
            for h in holder_data:
                addr_link = f"<a href='https://solscan.io/account/{h['address']}'>{h['address']}</a>"
                action = "kupio" if h["action"] == "buy" else "prodao"
                message_lines.append(
                    f"🔹 Holder #{h['rank']} {addr_link} je {action} {h['amount']:.4f} tokena u {h['timestamp']}."
                )
        else:
            message_lines.append("⚠️ <i>Nema aktivnosti holdera u poslednjih 1h.</i>")

        await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        print(f"[Greška u izveštaju] {e}")

@scheduler.scheduled_job("interval", hours=1)
def scheduled_task():
    asyncio.run(generate_report())

if __name__ == "__main__":
    asyncio.run(generate_report())
    scheduler.start()









