import httpx

async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana/AyCkqVLkmMnqYCrCh2fFB1xEj29nymzc5t6PvyRHaCKn"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            pair = data.get("pairs", [])[0]

            price = float(pair.get("priceUsd", 0))
            volume = pair.get("volume", {})  # ispravno polje

            # Pretpostavljamo da je ~50/50 raspodela ako nemamo detaljno
            buy_volumes = {
                "m5": volume.get("m5", 0) / 2,
                "h1": volume.get("h1", 0) / 2,
                "h6": volume.get("h6", 0) / 2,
                "h24": volume.get("h24", 0) / 2,
            }

            sell_volumes = {
                "m5": volume.get("m5", 0) / 2,
                "h1": volume.get("h1", 0) / 2,
                "h6": volume.get("h6", 0) / 2,
                "h24": volume.get("h24", 0) / 2,
            }

            return price, buy_volumes, sell_volumes
    except Exception as e:
        print(f"[Dexscreener error] {e}")
        return None, {}, {}
