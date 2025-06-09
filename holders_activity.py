import httpx
import os
from datetime import datetime, timedelta
from holders import TOP_HOLDERS

RPC_URL = os.getenv("RPC_URL")
DIS_TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"

async def get_holder_balances_and_activity():
    results = []
    most_active = {"address": None, "tx_count": 0}
    now = datetime.utcnow()

    async with httpx.AsyncClient(timeout=10.0) as client:
        for address in TOP_HOLDERS:
            try:
                # RPC payload za balans
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        address,
                        {"mint": DIS_TOKEN_MINT},
                        {"encoding": "jsonParsed"}
                    ]
                }

                r = await client.post(RPC_URL, json=payload)
                data = r.json()

                dis_balance = 0.0
                try:
                    dis_balance = data["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
                except Exception:
                    pass  # može ostati 0.0

                # Transakcije (koristimo Solscan kao pomoćni izvor)
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

                if activity_24h > most_active["tx_count"]:
                    most_active = {"address": address, "tx_count": activity_24h}

                results.append({
                    "address": address,
                    "dis_balance": dis_balance,
                    "tx_count_24h": activity_24h
                })

            except Exception as e:
                print(f"[ERROR] {address}: {e}")
                results.append({
                    "address": address,
                    "dis_balance": "error",
                    "tx_count_24h": "error"
                })

    return results, most_active
