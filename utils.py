import httpx
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DEX_PAIR_ADDRESS = "AyCkqVaYArj6uGvVhEqKUw6vY2BrZhS1F13ArLTVaCKn"

# ✅ Dohvata cenu i 24h obim trgovine sa Dexscreener-a
async def get_token_price_and_volume():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEX_PAIR_ADDRESS}"
            r = await client.get(url)
            data = r.json()

            if "pair" in data:
                price = float(data["pair"]["priceUsd"])
                volume = float(data["pair"]["volume"]["h24"])
                buy_volume = float(data["pair"]["buyVolume"]["h24"])
                sell_volume = float(data["pair"]["sellVolume"]["h24"])
                return price, volume, buy_volume, sell_volume
            else:
                print("[WARN] Pair nije pronađen")
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
