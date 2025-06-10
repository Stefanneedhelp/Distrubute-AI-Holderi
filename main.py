import os
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from datetime import datetime
import pytz

from utils import (
    get_token_price,
    fetch_global_volume_delta,
    send_telegram_message,
    get_dis_balance
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TOP_HOLDERS = [
    "DJVWifhSJoRWq8fPXRVJqbUjgAZphppSKsw9EedVuad6",
    "7MV6vtiFJPhHgBQc6Ch4hHCrYfXRr5xkbqEVUnomKXCK",
    "E5WchutHdCY8besK1gFg8Bc5AzXssZeDPKrNGWWemiiP",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF"
]

PREVIOUS_BALANCES = {addr: 0.0 for addr in TOP_HOLDERS}
LOCAL_TZ = pytz.timezone("Europe/Paris")

# ✅ Glavni izveštaj koji se šalje na svakih 5 minuta
async def generate_report():
    try:
        async with Bot(token=BOT_TOKEN) as bot:
            price = await get_token_price()
            volume = await fetch_global_volume_delta()

            if price is None:
                price = 0.0

            if volume is None:
                volume = {
                    "buy_volume": 0.0,
                    "sell_volume": 0.0,
                    "change_24h": 0.0
                }

            trend_emoji = "📈" if volume["change_24h"] > 0 else "📉"

            most_active_address = None
            largest_change = 0
            holder_lines = []

            for addr in TOP_HOLDERS:
                balance = await get_dis_balance(addr)
                previous = PREVIOUS_BALANCES.get(addr, 0.0)
                delta = balance - previous
                PREVIOUS_BALANCES[addr] = balance

                if abs(delta) > abs(largest_change):
                    largest_change = delta
                    most_active_address = addr

                if abs(delta) >= 10000:
                    holder_lines.append(
                        f"🔄 <b>{addr[:4]}...{addr[-4:]}</b> promena: {delta:.0f} DIS (trenutno: {balance:.0f})"
                    )

            if not holder_lines:
                holder_lines.append("ℹ️ Nema značajnih promena balansa među holderima.")

            message_lines = [
                f"{trend_emoji} <b>DIS Izveštaj (24h)</b>",
                f"💰 Cena: ${price:.6f}",
                f"🟢 Kupovine: ${volume['buy_volume']:.0f}",
                f"🔴 Prodaje: ${volume['sell_volume']:.0f}",
                "",
                "👤 <b>Najaktivniji holder:</b>",
                most_active_address if most_active_address else "Nema aktivnosti",
                "",
                "📦 <b>Promene balansa:</b>",
                *holder_lines,
                "",
                f"🔗 <a href='https://dexscreener.com/solana/ayckqvlkmnnqycrch2ffb1xej29nymzc5t6pvyrhackn'>Dexscreener link</a>"
            ]

            await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines))

    except Exception as e:
        print(f"[ERROR generate_report] {e}")

# ✅ Startuje scheduler i petlju
async def main():
    scheduler = AsyncIOScheduler(timezone=LOCAL_TZ)
    scheduler.add_job(generate_report, "interval", minutes=5)
    scheduler.start()

    print("[INFO] Bot je pokrenut i izveštaj ide svakih 5 minuta.")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
