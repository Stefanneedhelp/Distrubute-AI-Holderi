import httpx
from datetime import datetime, timedelta
from holders import TOP_HOLDERS

# Mint adresa za DIS token
DIS_TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"

async def get_holder_balances_and_activity():
    results = []
    most_active = {"address": None, "tx_count": 0}
    now = datetime.utcnow()

    async with httpx.AsyncClient(timeout=10.0) as client:
        for address in TOP_HOLDERS:
            try:
                # 1. Dohvati sve tokene adrese
                balance_url = f"https://public-api.solscan.io/account/tokens?account={address}"
                balance_resp = await client.get(balance_url)
                balances = balance_resp.json()
                dis_balance = 0

                for token in balances:
                    if token.get("tokenAddress") == DIS_TOKEN_MINT:
                        dis_balance = token.get("tokenAmount", {}).get("uiAmount", 0)
                        break

                # 2. Dohvati zadnjih 20 transakcija
                tx_url = f"https://public-api.solscan.io/account/transactions?address={address}&limit=20"
                tx_resp = await client.get(tx_url)
                transactions = tx_resp.json()
                activity_24h = 0

                for tx in transactions:
                    block_time = tx.get("blockTime")
                    if block_time:
                        tx_time = datetime.utcfromtimestamp(block_time)
                        if now - tx_time <= timedelta(hours=24):
                            activity_24h += 1

                # Proveri da li je najaktivniji
                if activity_24h > most_active["tx_count"]:
                    most_active = {"address": address, "tx_count": activity_24h}

                results.append({
                    "address": address,
                    "dis_balance": dis_balance,
                    "tx_count_24h": activity_24h
                })

            except Exception as e:
                results.append({
                    "address": address,
                    "dis_balance": "error",
                    "tx_count_24h": "error"
                })

    return results, most_active
