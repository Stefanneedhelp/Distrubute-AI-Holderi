import os
import httpx
from telegram.constants import ParseMode

# Dexscreener konfiguracija
PAIR_ADDRESS = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
DEX_API = f"https://api.dexscreener.com/latest/dex/pairs/solana/{PAIR_ADDRESS}"

# ✅ Dohvatanje cene tokena
async def get_token_price():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DEX_API)
            data = response.json()
            return float(data["pair"]["priceUsd"])
    except Exception as e:
        print(f"[Greška u get_token_price] {e}")
        return None

# ✅ Detekcija volumena u poslednjih 15 minuta
async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DEX_API)
            data = response.json()
            pair = data.get("pair", {})

            current_volume = float(pair.get("volumeUsd", 0.0))
            print("[DEBUG] Trenutni volumeUsd:", current_volume)

            prev_volume = float(os.environ.get("PREV_VOLUME", "0"))
            delta_volume = max(current_volume - prev_volume, 0)

            print(f"[INFO] PREV_VOLUME: {prev_volume} → NOVO: {current_volume}")

            # ⚠️ Info: ovo NE menja varijablu u Render Environment
            # Samo lokalno zapisuje ako se koristi .env fajl (opciono)
            with open(".env", "a") as f:
                f.write(f"\nPREV_VOLUME={current_volume}")

            return {
                "buy": delta_volume / 2,
                "sell": delta_volume / 2
            }

    except Exception as e:
        print(f"[Greška u fetch_global_volume_delta] {e}")
        return None

# ✅ Slanje poruke na Telegram
async def send_telegram_message(bot, chat_id, message):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        print("✅ Poruka poslata.")
    except Exception as e:
        print(f"❌ Greška u slanju poruke: {e}")


