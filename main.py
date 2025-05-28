import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from holders import HOLDERS
from utils import fetch_holder_transactions, get_token_price, fetch_global_volume, format_holder_report, send_telegram_message

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TOKEN_MINT = os.getenv("MONITORED_MINT")

scheduler = BackgroundScheduler(timezone="Europe/Belgrade")  # UTC+2


def daily_report():
    now = datetime.utcnow() + timedelta(hours=2)
    start_time = int((now - timedelta(minutes=1)).timestamp())
    end_time = int(now.timestamp())

    # Cena tokena
    price = get_token_price(TOKEN_MINT)

    # Aktivnosti holdera
    holder_activities = []
    for holder in HOLDERS:
        txs = fetch_holder_transactions(holder, TOKEN_MINT, start_time, end_time)
        if txs:
            holder_activities.append((holder, txs))

    # Ukupna market aktivnost
    global_stats = fetch_global_volume(TOKEN_MINT, start_time, end_time)

    # Formatiranje poruke
    report = f"\u2728 <b>Dnevni izve\u0161taj za {now.strftime('%d.%m.%Y %H:%M:%S')}</b> (UTC+2)\n"
    report += f"\n<b>Cena:</b> ${price:.6f}" if price else "\n<b>Cena:</b> N/A"
    
    if global_stats:
        total_buy, total_sell = global_stats
        total = total_buy + total_sell
        if total > 0:
            buy_pct = (total_buy / total) * 100
            sell_pct = (total_sell / total) * 100
            report += f"\n<b>Ukupno kupljeno:</b> ${total_buy:,.2f} ({buy_pct:.1f}%)"
            report += f"\n<b>Ukupno prodato:</b> ${total_sell:,.2f} ({sell_pct:.1f}%)"
    else:
        report += "\n<b>Ukupna aktivnost:</b> N/A"

    if holder_activities:
        report += "\n\n<b>Aktivnosti top holdera:</b>"
        for addr, txs in holder_activities:
            for tx in txs:
                time = datetime.utcfromtimestamp(tx['timestamp']) + timedelta(hours=2)
                report += f"\n- {tx['type']} sa <code>{tx['counterparty']}</code> u {time.strftime('%H:%M:%S')}"
    else:
        report += "\n\n<b>📭 Nema aktivnosti top holdera u prethodnih 24h.</b>"

    send_telegram_message(BOT_TOKEN, CHAT_ID, report)


scheduler.add_job(daily_report, "interval", minutes=1)
scheduler.start()

if __name__ == "__main__":
    print("📡 Bot pokrenut. Čeka vreme za izveštaj...")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
