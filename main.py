import asyncio
from holders_activity import get_holder_balances_and_activity
from utils import get_token_price, send_telegram_message

async def main():
    # Cena tokena
    dis_price = await get_token_price("2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf")

    # Aktivnosti i promene balansa
    changes, most_active = await get_holder_balances_and_activity()

    # Formatiraj poruku
    msg = "📉 DIS Izveštaj (24h)\n"
    msg += f"💵 Cena: ${dis_price:.6f}\n"
    msg += f"🟢 Kupovine: $0\n🔴 Prodaje: $0\n\n"

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

    await send_telegram_message(msg)

if __name__ == "__main__":
    asyncio.run(main())
