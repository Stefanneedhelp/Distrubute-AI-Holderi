import os
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
import pytz
from utils import (
    get_token_price,
    fetch_global_volume_delta,
    send_telegram_message,
    get_dis_balance,
    fetch_recent_trades,  # Nova funkcija
    format_number
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TOP_HOLDERS = [
    "DJVWifhSJoRWq8fPXRVJqbUjgAZphppSKsw9EedVuad6",
    "7MV6vtiFJPhHgBQc6Ch4hHCrYfXRr5xkbqEVUnomKXCK",
    "E5WchutHdCY8besK1gFg8Bc5AzXssZeDPKrNGWWemiiP",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF",
    "6FHi44dTMTsemG3SHvitgLBDEeJjHamfbc7dzwyCvpK2",
    "UD3oWFYRxmLH7gH2148bnv6UwLWTmg3ZfRYwdRCwsj8",
    "7PypumCQ4wco2bV4UAjCwbrdCdnWwyAacjxRhX3yuz8R",
    "CKhPzjCE8BE4BPior7RdUpDvjRx75Zt6RsVA9jdHVLy8",
    "C3QpoYdQfkyEH5ngZ29Ws7Gb45WTE48njS8DfwSdJexm",
    "9JHEUakXY3wGnQuRaV4uJQPY5nu81ndJ1fHxZZqNH798",
    "9LwsPtQLsZxH2RXiRcTRPVr3fsuyz2SsFdxvccfm4Gqs",
    "GB2HmT2tPSvksGt7QN46TYpmqcyhcQm89d6TyJtNwQ3L",
    "G1toYqBwHz1ou9za6sTNsWAkA7eUenNt2irm94T4Pr5a",
    "8V9FrBAvMjn4c7cDkMGTgYqVekBZVkKe3GguaqrNWpTM",
    "2WxdxZ9bhaCU2mPssvZZytmD5dZZfYs7wFnne63iZHmE",
    "7JWnEjndB1tiedTZW6oriQbkv1YhAvCt3ri6FP7xx576",
    "3cdFmMUdNev6y2WRvSkeFEc263Nfmzf2ZTTTwAJMnnAf",
    "GybhvUZzTq4qYBc292dz4HE4oQPZJGC9xGJdEH9uYeHK",
    "6dvpMLzunxUDybws6giNnPJ5nxpwvuugovsyPs6VzVdV",
    "12Gq9SpDoLPFEjuBVwu1zJZJtwNQj4Bqnn3uCAiGkm2T"
]

PREVIOUS_BALANCES = {addr: 0.0 for addr in TOP_HOLDERS}
LOCAL_TZ = pytz.timezone("Europe/Paris")

async def generate_report():
    try:
        async with Bot(token=BOT_TOKEN) as bot:
            price = await get_token_price()
            volume = await fetch_global_volume_delta()
            recent_trades = await fetch_recent_trades()

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
                        f"🔄 <b><a href='https://solscan.io/account/{addr}'>{addr[:4]}...{addr[-4:]}</a></b> promena: {format_number(delta)} DIS (trenutno: {format_number(balance)})"
                    )

            if not holder_lines:
                holder_lines.append("ℹ️ Nema značajnih promena balansa među holderima.")

            trade_lines = []
            for trade in recent_trades:
                typ = "🟢 Kupovina" if trade["type"] == "buy" else "🔴 Prodaja"
                amount = trade.get("amount", "N/A")
                address = trade.get("to") if trade["type"] == "buy" else trade.get("from")
                short_addr = f"{address[:4]}...{address[-4:]}"
                link = f"https://solscan.io/account/{address}"

                trade_lines.append(
                    f"{typ} - <a href='{link}'>{short_addr}</a>: {format_number(amount)} DIS"
                )

            if not trade_lines:
                trade_lines.append("ℹ️ Nema kupovina ili prodaja u zadnjih 5 minuta.")

            message_lines = [
                f"{trend_emoji} <b>DIS Izveštaj (24h)</b>",
                f"💰 Cena: ${price:.6f}",
                f"🟢 Kupovine: ${format_number(volume['buy_volume'])}",
                f"🔴 Prodaje: ${format_number(volume['sell_volume'])}",
                "",
                "👤 <b>Najaktivniji holder:</b>",
                f"<a href='https://solscan.io/account/{most_active_address}'>{most_active_address}</a>" if most_active_address else "Nema aktivnosti",
                "",
                "📦 <b>Promene balansa:</b>",
                *holder_lines,
                "",
                "📊 <b>Nove kupovine/prodaje (5m):</b>",
                *trade_lines,
                "",
                f"🔗 <a href='https://dexscreener.com/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn'>Dexscreener link</a>"
            ]

            await send_telegram_message(bot, CHAT_ID, "\n".join(message_lines), parse_mode="HTML")

    except Exception as e:
        print(f"[ERROR generate_report] {e}")

async def main():
    scheduler = AsyncIOScheduler(timezone=LOCAL_TZ)
    scheduler.add_job(generate_report, "interval", minutes=5)
    scheduler.start()

    print("[INFO] Bot je pokrenut i izveštaj ide svakih 5 minuta.")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
