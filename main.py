from datetime import datetime, timedelta
import os
from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message
from apscheduler.schedulers.blocking import BlockingScheduler

# Učitavanje okruženja
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MONITORED_MINT = os.getenv("MONITORED_MINT")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

# Lista adresa koje pratimo
from holders import HOLDERS

scheduler = BlockingScheduler(timezone="Europe/Paris", max_instances=1)

@scheduler.scheduled_job("interval", minutes=2)  # Za testiranje svakih 2 minuta

def generate_report():
    print("\n📡 Bot pokrenut. Čeka vreme za izveštaj...")

    now = datetime.utcnow() + timedelta(hours=2)  # UTC+2
    start_time = int((now - timedelta(hours=12)).timestamp())
    end_time = int(now.timestamp())

    print(f"🕕 Vremenski okvir: {datetime.utcfromtimestamp(start_time)} - {datetime.utcfromtimestamp(end_time)}")

    all_transactions = []
    for holder in HOLDERS:
        txs = fetch_holder_transactions(holder, MONITORED_MINT, HELIUS_API_KEY, start_time, end_time)
        all_transactions.extend(txs)

    if not all_transactions:
        summary = (
            f"📊 <b>Dnevni izveštaj</b> ({now.strftime('%Y-%m-%d %H:%M')})\n"
            f"<b>Cena:</b> ${get_token_price():.6f}\n"
            f"<b>Ukupno kupljeno:</b> $0.00\n"
            f"<b>Ukupno prodato:</b> $0.00\n"
            f"<b>Odnos kupovina/prodaja:</b> 0.00\n\n"
            f"📭 <b>Nema aktivnosti holdera</b>"
        )
        send_telegram_message(summary)
        return

    total_buy = sum(tx["usd_value"] for tx in all_transactions if tx["type"] == "BUY")
    total_sell = sum(tx["usd_value"] for tx in all_transactions if tx["type"] == "SELL")
    ratio = round(total_buy / total_sell, 2) if total_sell > 0 else "∞"
    token_price = get_token_price()

    summary = (
        f"📊 <b>Dnevni izveštaj</b> ({now.strftime('%Y-%m-%d %H:%M')})\n"
        f"<b>Cena:</b> ${token_price:.6f}\n"
        f"<b>Ukupno kupljeno:</b> ${total_buy:,.2f}\n"
        f"<b>Ukupno prodato:</b> ${total_sell:,.2f}\n"
        f"<b>Odnos kupovina/prodaja:</b> {ratio}"
    )
    send_telegram_message(summary)

    for tx in all_transactions:
        index = HOLDERS.index(tx["owner"]) + 1 if tx["owner"] in HOLDERS else "?"
        ts = datetime.utcfromtimestamp(tx["timestamp"]) + timedelta(hours=2)
        msg = (
            f"👤 <b>{tx['type']}</b> #{index}\n"
            f"• Adresa: <a href='https://solscan.io/account/{tx['owner']}'>{tx['owner'][:6]}...{tx['owner'][-4:]}</a>\n"
            f"• Količina: {tx.get('token_amount', 0):,.2f} tokena\n"
            f"• Vrednost: ${tx['usd_value']:,.2f}\n"
            f"• Interakcija sa: {tx['interaction_with']}\n"
            f"• Vreme: {ts.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_telegram_message(msg)

if __name__ == "__main__":
    scheduler.start()



