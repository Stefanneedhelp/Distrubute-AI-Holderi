import asyncio
from holders_activity import get_holder_balances_and_activity
from utils import get_token_price, send_telegram_message
from track_meteora import get_recent_swaps_by_balance

async def main():
    # Cena tokena (BirdEye)
    price = await get_token_price()

    # Aktivnosti holdera
    changes, most_active = await get_holder_balances_and_activity()

    # Meteora kupovine/prodaje na osnovu balansa
    dis_in, dis_out = await get_recent_swaps_by_balance()

    # Format poruke
    msg = "📊 DIS Dnevni Izveštaj (24h)\n"
    msg += f"💵 Cena: ${price:.6f}\n"
    msg += f"🟢 Kupovine (Meteora): {dis_out:,.1f} DIS = ${dis_out * price:,.0f}\n"
    msg += f"🔴 Prodaje (Meteora): {dis_in:,.1f} DIS = ${dis_in * price:,.0f}\n\n"

    # Najaktivniji holder
    if most_active:
        msg += f"👤 Najaktivniji holder:\n{most_active['address']}\n\n"
    else:
        msg += "👤 Najaktivniji holder: Nema aktivnosti u poslednjih 24h\n\n"

    # Promene balansa
    if not changes:
        msg += "📦 Nema značajnih promena balansa među holderima.\n"
    else:
        msg += "📦 Promene balansa:\n"
        for c in changes:
            msg += f"🔄 {c['address'][:4]}...{c['address'][-4:]} promena: {round(c['change'] / 1_000_000, 1)}M DIS "
            msg += f"(trenutno: {round(c['dis_balance'] / 1_000_000, 1)}M)\n"

    # Pošalji poruku
    await send_telegram_message(msg)

if __name__ == "__main__":
    asyncio.run(main())
