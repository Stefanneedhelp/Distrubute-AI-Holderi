import httpx
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DIS_MINT = os.getenv("DIS_MINT")

# ✅ Dohvata cenu i volume koristeći /search endpoint
async def get_token_price_and_volume():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.dexscreener.com/latest/dex/search?q={DIS_MINT}"
            r = await client.get(url)

            if r.status_code != 200:
                print(f"[WARN] Dexscreener returned {r.status_code}")
                return 0.0, 0.0, 0.0, 0.0

            data = r.json()
            if "pairs" in data and data["pairs"]:
                pair = data["pairs"][0]
                price = float(pair["priceUsd"])
                volume = float(pair["volume"]["h24"])
                buy_volume = float(pair["buyVolume"]["h24"])
                sell_volume = float(pair["sellVolume"]["h24"])
                return price, volume, buy_volume, sell_volume
            else:
                print("[WARN] No pair found in Dexscreener search")
                return 0.0, 0.0, 0.0, 0.0
    except Exception as e:
        print(f"[ERROR get_token_price_and_volume] {e}")
        return 0.0, 0.0, 0.0, 0.0

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
