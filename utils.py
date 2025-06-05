import httpx
import os

DEX_API_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"

async def fetch_global_volume():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(DEX_API_URL)
            data = resp.json()

            pair = data.get("pair")
            if not pair:
                return None

            volume_usd = float(pair.get("volumeUsd", 0))

            txns = pair.get("txns", {}).get("m5", {})
            buys = float(txns.get("buys", 0))
            sells = float(txns.get("sells", 0))
            total = buys + sells

            if total == 0:
                return {"buy": volume_usd / 2, "sell": volume_usd / 2}

            buy_ratio = buys / total
            buy_volume = volume_usd * buy_ratio
            sell_volume = volume_usd * (1 - buy_ratio)

            return {
                "buy": buy_volume,
                "sell": sell_volume
            }

    except Exception as e:
        print(f"[Greška u fetch_global_volume]: {e}")
        return None

async def get_token_price():
    try:
        async with httpx.AsyncClient() as client:
            url = DEX_API_URL
            response = await client.get(url)
            data = response.json()
            return float(data.get("pair", {}).get("priceUsd", 0))
    except Exception as e:
        print(f"❌ Greška u dohvatanju cene: {e}")
        return None

async def send_telegram_message(bot, chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Greška u slanju poruke: {e}")





