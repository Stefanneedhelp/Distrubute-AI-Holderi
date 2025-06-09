from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from telegram import Bot
import os
import asyncio

from utils import fetch_dexscreener_data, get_dexscreener_link
from holders_activity import get_holder_balances_and_activity

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
scheduler = BlockingScheduler(timezone="Europe/Paris")

async def generate_report():
    try:
        async with Bot(token=TOKEN) as bot:
            # 1. Cena i volume
            price, buy_24h, sell_24h = await fetch_dexscreener_data()
            dexscreener_link = get_dexscreener_link()

            # 2. Holderi
            holders_data, most_active = await get_holder_balances_and_activity()

            # 3. Aktivnost
            if all(h["tx_count_24h"] == 0 for h in holders_data):
                holder_lines = ["📭 <b>Nema aktivnosti holdera u poslednjih 24h</b>"]
            else:
                holder_lines = [
                    f"🏃‍♂️ <b>Najaktivniji holder:</b> {most_active['address']} ({most_active['tx_count']} tx)"
                ]
                for h in holders_data:
                    if isinstance(h["tx_count_24h"], int) and h["tx_count_24h"] > 0:
                        holder_lines.append(
                            f"• {h['address'][:5]}...{h['address'][-5:]} | 💼 {h['dis_balance']:.2f} DIS | 🔁 {h['tx_count_24h']} tx"
                        )

            # 4. Top 5 holdera po balansu
            top_5 = sorted(
                [h for h in holders_data if isinstance(h["dis_balance"], (int, float))],
                key=lambda x: x["dis_balance"],
                reverse=True
            )[:5]

            top_5_lines = ["🏦 <b>Top 5 holdera (DIS balans):</b>"]
            for h in top_5:
                short = f"{h['address'][:5]}...{h['address'][-5:]}"
                bal = f"{h['dis_balance']:,.2f}"
                top_5_lines.append(f"• {short} → {bal} DIS")

            # 5. Konačna poruka
            message_lines = [
                f"📈 <b>Izveštaj za DIS token (24h)</b>",
                f"💰 Cena: ${price:.6f}",
                f"🟢 <b>Kupovine:</b> ${buy_24h:,.2f}",
                f"🔴 <b>Prodaje:</b> ${sell_24h:,.2f}",
                "",
                *holder_lines,
                "",
                *top_5_lines,
                "",
                f"🔗 <a href=\"{dexscreener_link}\">Dexscreener DIS/SOL</a>"
            ]

            await bot.send_message(chat_id=CHAT_ID, text="\n".join(message_lines), parse_mode="HTML")

    except Exception as e:
        print(f"[Bot error] {e}")

@scheduler.scheduled_job('interval', minutes=5)
def scheduled_job():
    asyncio.run(generate_report())

if __name__ == "__main__":
    scheduler.start()

