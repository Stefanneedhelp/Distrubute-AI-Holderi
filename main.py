import asyncio
from datetime import datetime
from telegram import Bot
from utils import (
    get_token_price,
    fetch_global_volume_delta,
    send_telegram_message,
)
from holders_activity import get_holder_balances_and_activity
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
chat_id = os.getenv("CHAT_ID")

async def generate_report():
    try:
        price = await get_token_price()
        volume_data = await fetch_global_volume_delta()
        holders, most_active = await get_holder_balances_and_activity()

        message_lines = []
        message_lines.append("ðŸ“ˆ <b>IzveÅ¡taj za DIS token (24h)</b>")
        message_lines.append(f"ðŸ’° <b>Cena:</b> ${price:.6f}")
        message_lines.append(f"ðŸ“‰ <b>Promena u 24h:</b> {volume_data['change_24h']}%")
        message_lines.append(f"ðŸŸ¢ <b>Kupovine:</b> ${volume_data['buy_volume']:,}")
        message_lines.append(f"ðŸ”´ <b>Prodaje:</b> ${volume_data['sell_volume']:,}")

        # Najaktivniji holder
        holder_tag = "None" if not most_active["address"] else most_active["address"][:4] + "..."
        message_lines.append(f"ðŸƒâ€â™‚ï¸ <b>Najaktivniji holder:</b> {holder_tag} ({most_active['tx_count']} tx)")

        # Top 5 holdera
        message_lines.append("ðŸ’µ <b>Top 5 holdera (DIS balans):</b>")
        for h in holders[:5]:
            balance_str = f"{h['dis_balance']:,}" if isinstance(h['dis_balance'], (float, int)) else h['dis_balance']
            message_lines.append(f"â€¢ {h['address'][:4]}... â€“ {balance_str} DIS")

        # Dexscreener link
        message_lines.append("ðŸ”— <a href='https://dexscreener.com/solana/ayckqvlkmnnqycrch2ffb1xej29nymzc5t6pvyrhackn'>Dexscreener DIS/SOL</a>")

        message = "\n".join(message_lines)
        await send_telegram_message(bot, chat_id, message)
    except Exception as e:
        print(f"[ERROR generate_report] {e}")

if __name__ == "__main__":
    asyncio.run(generate_report())
