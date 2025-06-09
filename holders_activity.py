import httpx
import os
from datetime import datetime, timedelta
from holders import TOP_HOLDERS

RPC_URL = os.getenv("RPC_URL")
DIS_TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"

# 🔄 Funkcija koja dohvata tačan DIS balans za adresu
async def get_dis_balance(address: str) -> float:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Nađi DIS token account
            payload_accounts = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    address,
                    {"mint": DIS_TOKEN_MINT},
                    {"encoding": "jsonParsed"}
                ]
            }

            r1 = await client.post(RPC_URL, json=payload_accounts)
            token_accounts = r1.json()["result"]["value"]

            if not token_accounts:
                return 0.0

            token_account_address = token_accounts[0]["pubkey"]

            # 2. Dohvati balans tog account-a
            payload_balance = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountBalance",
                "params": [token_account_address]
            }

            r2 = await client.post(RPC_URL, json=payload_balance)
            balance_data = r2.json()
            ui_amount = balance_data["result"]["value"]["uiAmount"]

            return float(ui_amount)
    except Exception as e:
        print(f"[ERROR get_dis_balance] {address}: {e}")
        return 0.0

# 📊 Glavna funkcija za prikaz holdera
async def get_holder_balances_and_activity():
    results = []
    most_active = {"address": None, "tx_count": 0}
    now = datetime.utcnow()

    async with httpx.AsyncClient(timeout=10.0) as client:
        for address in TOP_HOLDERS:
            try:
                # 1. DIS balans
                dis_balance = await get_dis_balance(address)
                print(f"[DEBUG] {address} balans: {dis_balance}")

                # 2. Aktivnost (Solscan poslednjih 20 tx)
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

                print(f"[DEBUG] {address} tx u 24h: {activity_24h}")

                if activity_24h > most_active["tx_count"]:
                    most_active = {"address": address, "tx_count": activity_24h}

                results.append({
                    "address": address,
                    "dis_balance": dis_balance,
                    "tx_count_24h": activity_24h
                })

            except Exception as e:
                print(f"[ERROR holder check] {address}: {e}")
                results.append({
                    "address": address,
                    "dis_balance": "error",
                    "tx_count_24h": "error"
                })

    return results, most_active
