import httpx
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DIS_MINT = os.getenv("DIS_MINT")

# ✅ Dohvata cenu tokena preko Jupiter API-ja
async def get_token_price():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://price.jup.ag/v4/price?ids={DIS_MINT}"
            r = await client.get(url)
            if r.status_code != 200:
                print(f"[WARN] Jupiter API error {r.status_code}")
                return 0.0

            data = r.json()
            if DIS_MINT in data:
                price = float(data[DIS_MINT]["price"])
                return price
            else:
                print(f"[WARN] Jupiter ne vraća podatke za {DIS_MINT}")
                return 0.0
    except Exception as e:
        print(f"[ERROR get_token_price] {e}")
        return 0.0

# 📤 Šalje poruku na Telegram
async def send_telegram_message(text: str) -> None:
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"[ERROR send_telegram_message] {e}")
