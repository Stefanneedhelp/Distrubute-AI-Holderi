import httpx

# Fetch price i volume iz Dexscreener API-ja
async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            pair = data.get("pair", {})

            price = float(pair.get("priceUsd", 0))
            buy_volume = pair.get("volumeUsd", {}).get("m15", {}).get("buy", 0)
            sell_volume = pair.get("volumeUsd", {}).get("m15", {}).get("sell", 0)

            return price, buy_volume, sell_volume
    except Exception as e:
        print(f"[Dexscreener error] {e}")
        return None, 0.0, 0.0
