import httpx
from collections import defaultdict

DEXSCREENER_URL = "https://dexscreener.com/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"

async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            pair = data.get("pairs", [])[0]

            price = float(pair.get("priceUsd", 0))
            buy_volume_24h = float(pair.get("buyVolume", 0))
            sell_volume_24h = float(pair.get("sellVolume", 0))

            return price, buy_volume_24h, sell_volume_24h
    except Exception as e:
        print(f"[Dexscreener error] {e}")
        return None, 0.0, 0.0

def get_dexscreener_link():
    return DEXSCREENER_URL
