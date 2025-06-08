import os
import httpx
import json
from telegram.constants import ParseMode

PAIR_ADDRESS = "AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
DEX_API = f"https://api.dexscreener.com/latest/dex/pairs/solana/{PAIR_ADDRESS}"
STATE_FILE = "state.json"

# Cena tokena
async def get_token_price():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DEX_API)
            data = response.json()
            return float(data["pair"]["priceUsd"])
    except Exception as e:
        print(f"[Greška u get_token_price] {e}")
        return None

# Globalni volumen tokena
async def fetch_global_volume_delta():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DEX_API)
            data = response.json()
            txns = data.get("pair", {}).get("txns", {})
            if not txns:
                return None

            current_buy = float(txns.get("m5", {}).get("buyVolume", 0.0))
            current_sell = float(txns.get("m5", {}).get("sellVolume", 0.0))

            # Učitaj prethodno stanje
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
            else:
                state = {"prev_buy": 0, "prev_sell": 0}

            delta = {
                "buy": max(current_buy - state["prev_buy"], 0),
                "sell": max(current_sell - state["prev_sell"], 0),
            }

            # Sačuvaj trenutno stanje
            with open(STATE_FILE, "w") as f:
                json.dump({"prev_buy": current_buy, "prev_sell": current_sell}, f)

            return delta

    except Exception as e:
        print(f"[Greška u fetch_global_volume_delta] {e}")
        return None

# Slanje poruke
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




