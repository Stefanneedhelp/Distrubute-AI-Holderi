import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, send_telegram_message
from holders import HOLDERS

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MONITORED_MINT = os.getenv("MONITORED_MINT")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

scheduler = BlockingScheduler(
    timezone="Europe/Paris",
    max_instances=1,
    coalesce=True,
    misfire_grace_time=60
)

@scheduler.scheduled_job("interval", minutes=2)
# Kasnije promeniti u cron: hour=6, minute=0
def generate_report():
    print("\n📡 Bot pokrenut. Čeka vreme za izveštaj...")

    now = datetime.utcnow() + timedelta(hours=2)  # lokalno vreme (CEST)
    start_time = int((now - timedelta(hours=12)).timestamp())
    end_time = int(now.timestamp())

    print(f"🕕 Vremenski okvir: {datetime.utcfromtimestamp(start_time)} - {datetime.utcfromtimestamp(end_time)}")

    # 1. Aktivnosti holdera
    holder_msgs = []
    for index, holder in enumerate(HOLDERS):
        txs = fetch_holder_transactions(holder, MONITORED_MINT, HELIUS_API_KEY, start_time, end_time)
        for tx in txs:
            t_type = tx.get("type", "Interakcija")
            ts = datetime.utcfromtimestamp(tx["timestamp"]) + timedelta(hours=2)
            amount = tx.get("token_amount", 0)
            msg = (
                f"👤 <b>{t_type}</b> | Holder #{index+1}\n"
                f"• <a href='https://solscan.io/account/{holder}?cluster=mainnet'>{holder}</a>\n"
                f"• Količina: {amount:,.2f} tokena\n"
                f"• Interakcija sa: {tx['interaction_with']}\n"
                f"• Vreme: {ts.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            holder_msgs.append(msg)

    if not holder_msgs:
        holder_msgs.append("📭 <b>Nema aktivnosti holdera</b>")

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
    for m in holder_msgs:
        send_telegram_message(m)

if __name__ == "__main__":
    scheduler.start()




