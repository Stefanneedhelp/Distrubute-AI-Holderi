import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MONITORED_ADDRESSES = os.getenv("MONITORED_ADDRESSES", "").split(",")


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data)


def fetch_transactions(address, start_time, end_time):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={os.getenv('HELIUS_API_KEY')}"
        response = requests.get(url)
        transactions = response.json()

        holder_activities = []
        for tx in transactions:
            ts = datetime.fromtimestamp(tx.get("timestamp", 0))
            if start_time <= ts <= end_time:
                for transfer in tx.get("nativeTransfers", []):
                    if transfer.get("fromUserAccount") == address:
                        amount = transfer.get("amount", 0) / 1_000_000_000
                        holder_activities.append(f"{address} poslao {amount:.4f} SOL")
                    elif transfer.get("toUserAccount") == address:
                        amount = transfer.get("amount", 0) / 1_000_000_000
                        holder_activities.append(f"{address} primio {amount:.4f} SOL")

        return holder_activities
    except Exception as e:
        print(f"[Fetch Error] {e}")
        return []


def main():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)

    all_activities = []
    for idx, addr in enumerate(MONITORED_ADDRESSES):
        activities = fetch_transactions(addr, start_time, end_time)
        if activities:
            all_activities.append(f"👤 Holder #{idx + 1}: <a href='https://solscan.io/account/{addr}'>{addr}</a>")
            all_activities.extend(activities)

    if not all_activities:
        send_telegram_message("📭 Nema aktivnosti holdera u prethodna 24h.")
    else:
        send_telegram_message("\n".join(all_activities))


if __name__ == "__main__":
    main()






