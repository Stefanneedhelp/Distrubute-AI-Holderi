import httpx

async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            pair = data.get("pairs", [])[0]

            price = float(pair.get("priceUsd", 0))

            volume_usd = pair.get("volumeUsd", {})
            buy_volumes = {
                "m5": volume_usd.get("m5", {}).get("buy", 0),
                "h1": volume_usd.get("h1", {}).get("buy", 0),
                "h6": volume_usd.get("h6", {}).get("buy", 0),
                "h24": volume_usd.get("h24", {}).get("buy", 0),
            }

            sell_volumes = {
                "m5": volume_usd.get("m5", {}).get("sell", 0),
                "h1": volume_usd.get("h1", {}).get("sell", 0),
                "h6": volume_usd.get("h6", {}).get("sell", 0),
                "h24": volume_usd.get("h24", {}).get("sell", 0),
            }

            return price, buy_volumes, sell_volumes
    except Exception as e:
        print(f"[Dexscreener error] {e}")
        return None, {}, {}
