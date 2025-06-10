import httpx
import os
import json
import asyncio
from datetime import datetime, timedelta
from holders import TOP_HOLDERS

RPC_URL = os.getenv("RPC_URL")
DIS_TOKEN_MINT = "2AEU9yWk3dEGnVwRaKv4div5TarC4dn7axFLyz6zG4Pf"
BALANCES_FILE = "balances.json"
BALANCE_THRESHOLD = 10000  # DIS promena koja se beleži

# Učitaj prethodne balanse
def load_previous_balances():
    if os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, "r") as f:
            return json.load(f)
    return {}

# Sačuvaj nove balanse
def save_current_balances(data):
    with open(BALANCES_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 🔄 Dohvati tačan DIS balans za adresu
async def get_dis_balance(address: str) -> float:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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

# 📊 Glavna funkcija
async def get_holder_balances_and_activity():
    results = []
    most_active = {"address": None, "tx_count": 0}
    now = datetime.utcnow()
    previous_balances = load_previous_balances()

    async with httpx.AsyncClient(timeout=10.0) as client:
        for address in TOP_HOLDERS:
            try:
                dis_balance = await get_dis_balance(address)
                print(f"[DEBUG] {address} balans: {dis_balance}")

                # Aktivnost iz Solscan API-ja
                tx_url = f"https://public-api.solscan.io/account/transactions?address={address}&limit=20"
                tx_resp = await client.get(tx_url)

                if tx_resp.status_code != 200:
                    print(f"[WARN] Solscan error {tx_resp.status_code} za {address}")
                    transactions = []
                else:
                    try:
                        transactions = tx_resp.json()
                    except Exception as e:
                        print(f"[ERROR Solscan JSON] {address}: {e}")
                        transactions = []

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

                # Promena balansa
                prev_balance = float(previous_balances.get(address, 0.0))
                balance_diff = dis_balance - prev_balance

                if abs(balance_diff) >= BALANCE_THRESHOLD:
                    results.append({
                        "address": address,
                        "dis_balance": dis_balance,
                        "change": balance_diff,
                        "tx_count_24h": activity_24h
                    })

                await asyncio.sleep(0.2)  # Pauza da izbegnemo rate limit

            except Exception as e:
                print(f"[ERROR holder check] {address}: {e}")

    # Snimi nova stanja
    save_current_balances({
        address: round(await get_dis_balance(address), 2)
        for address in TOP_HOLDERS
    })

    return results, most_active if most_active["tx_count"] > 0 else None
