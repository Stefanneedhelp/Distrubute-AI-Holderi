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
            f"ðŸ“ˆ *IzveÅ¡taj za poslednjih 1h*",
            f"ðŸ’° Cena tokena: ${token_price:.6f}" if token_price else "ðŸ’° Cena tokena: Nepoznata",
            f"ðŸ”„ Ukupno kupljeno: ${total_volume['buy']:.2f}" if total_volume else "ðŸ”„ Ukupno kupljeno: Nepoznato",
            f"ðŸ”» Ukupno prodato: ${total_volume['sell']:.2f}" if total_volume else "ðŸ”» Ukupno prodato: Nepoznato",
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
            message_lines.append("\nðŸ‘¥ Aktivnosti top holdera:\n")
            for h in holder_data:
                addr_link = f"[{h['address']}](https://solscan.io/account/{h['address']})"
                action = "kupio" if h["action"] == "buy" else "prodao"
                message_lines.append(
                    f"ðŸ”¹ Holder #{h['rank']} {addr_link} je {action} {h['amount']:.4f} tokena u {h['timestamp']}."
                )
        else:
            message_lines.append("âš ï¸ Nema aktivnosti holdera u poslednjih 1h.")

        await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        print(f"[GreÅ¡ka u izveÅ¡taju] {e}")

@scheduler.scheduled_job("interval", hours=1)
def scheduled_task():
    asyncio.run(generate_report())

if __name__ == "__main__":
    asyncio.run(generate_report())  # Run once on startup
    scheduler.start()









