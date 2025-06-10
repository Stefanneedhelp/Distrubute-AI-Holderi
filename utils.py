import httpx
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DIS_MINT = os.getenv("DIS_MINT")

# ✅ BirdEye API – vraća cenu i ukupan volume (bez buy/sell)
async def get_token_price_and_volume():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Cena
            url = f"https://public-api.birdeye.so/public/price?address={DIS_MINT}"
            r = await client.get(url)
            if r.status_code != 200:
                print(f"[WARN] BirdEye price error {r.status_code}")
                return 0.0, 0.0, 0.0, 0.0

            data = r.json()
            price = float(data["data"]["value"])

            # Volume
            v_url = f"https://public-api.birdeye.so/public/token/volume?address={DIS_MINT}"
            v_resp = await client.get(v_url)
            if v_resp.status_code == 200:
                v_data = v_resp.json()
                volume = float(v_data["data"]["volume24hQuote"])
            else:
                volume = 0.0

            return price, volume, 0.0, 0.0

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
