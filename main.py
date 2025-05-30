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

scheduler = BlockingScheduler(timezone="Europe/Paris")

@scheduler.scheduled_job("interval", minutes=1)  # Promeni na cron nakon testiranja
def generate_report():
    print("\n📡 Bot pokrenut. Čeka vreme za izveštaj...")

    now = datetime.utcnow() + timedelta(hours=2)  # UTC+2
    start_time = int((now - timedelta(hours=12)).timestamp())
    end_time = int(now.timestamp())

    print(f"🕕 Vremenski okvir: {datetime.utcfromtimestamp(start_time)} - {datetime.utcfromtimestamp(end_time)}")

    # 1. Aktivnosti holdera
    holder_msgs = []
    for holder in HOLDERS:
        txs = fetch_holder_transactions(holder, MONITORED_MINT, HELIUS_API_KEY, start_time, end_time)
        for tx in txs:
            t_type = tx.get("type", "Interakcija")
            ts = datetime.utcfromtimestamp(tx["timestamp"]) + timedelta(hours=2)
            msg = f"👤 <b>{t_type}</b>\n• Adresa: {holder}\n• Interakcija sa: {tx['interaction_with']}\n• Vreme: {ts.strftime('%Y-%m-%d %H:%M:%S')}"
            holder_msgs.append(msg)

    # 2. Cene i globalne kupovine/prodaje
    price = get_token_price()
    buy_total, sell_total = fetch_global_volume(MONITORED_MINT, HELIUS_API_KEY, start_time, end_time)

    # 3. Slanje izveštaja
    summary = (
        f"📊 <b>Dnevni izveštaj</b> ({now.strftime('%Y-%m-%d %H:%M')})\n"
        f"<b>Cena:</b> ${price:.6f}\n"
        f"<b>Ukupno kupljeno:</b> ${buy_total:,.2f}\n"
        f"<b>Ukupno prodato:</b> ${sell_total:,.2f}\n"
        f"<b>Odnos kupovina/prodaja:</b> {buy_total / (sell_total or 1):.2f}"
    )

    send_telegram_message(summary)

    if holder_msgs:
        for m in holder_msgs:
            send_telegram_message(m)
    else:
        send_telegram_message("📭 <b>Nema aktivnosti holdera</b>")

if __name__ == "__main__":
    scheduler.start()

