import requests
import os
import time

# Učitavanje API ključa iz Render environment varijabli
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# Stavi ovde tačan pair address za DIS/SOL na Meteori (kopira se sa Birdeye stranice)
PAIR_ADDRESS = "4nGVZkDUo3hH2RS1GSZoGh8E1hJW6W8isCJKosN4kJGe"  # primer

def get_timestamp_24h_ago():
    return int(time.time()) - 86400  # vreme pre 24 sata

async def get_recent_swaps():
    url = f"https://public-api.birdeye.so/defi/trade-history/pair/{PAIR_ADDRESS}?from={get_timestamp_24h_ago()}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": BIRDEYE_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        trades = data.get("data", [])

        dis_in, dis_out = 0.0, 0.0

        for trade in trades:
            if trade.get("side") == "buy":
                dis_out += float(trade.get("baseAmount", 0))
            elif trade.get("side") == "sell":
                dis_in += float(trade.get("baseAmount", 0))

        return dis_in, dis_out

    except Exception as e:
        print("[ERROR get_recent_swaps]", e)
        return 0.0, 0.0
