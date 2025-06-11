import asyncio
from holders_activity import get_holder_balances_and_activity
from utils import get_token_price, send_telegram_message
from track_meteora import get_recent_swaps

async def main():
    # Cena tokena
    price = await get_token_price()

    # Promene balansa holdera (bez transakcija)
    changes, _ = await get_holder_balances_and_activity()

    # Meteora kupovine/prodaje
    dis_in, dis_out = await get_recent_swaps()

    # Format poruke
    msg = "📊 DIS Dnevni Izveštaj (24h)\n"
    msg += f"💵 Cena: ${price:.6f}\n"
    msg += f"🟢 Kupovine (Meteora): {dis_out:,.1f} DIS = ${dis_out * price:,.0f}\n"
    msg += f"🔴 Prodaje (Meteora): {dis_in:,.1f} DIS = ${dis_in * price:,.0f}\n\n"

    # Promene balansa
    if not changes:
        msg += "📦 Nema značajnih promena balansa među holderima.\n"
    else:
        msg += "📦 Promene balansa:\n"
        for c in changes:
            msg += f"🔄 {c['address'][:4]}...{c['address'][-4:]} promena: {round(c['change'] / 1_000_000, 1)}M DIS "
            msg += f"(trenutno: {round(c['dis_balance'] / 1_000_000, 1)}M)\n"

    # Pošalji poruku na Telegram
    await send_telegram_message(msg)

if __name__ == "__main__":
    asyncio.run(main())
