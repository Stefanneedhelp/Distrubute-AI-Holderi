
import os
import httpx
from datetime import datetime, timedelta
from holders import TOP_HOLDERS

RPC_URL = os.getenv("RPC_URL")
DIS_TOKEN_MINT = os.getenv("DIS_MINT")

# Cache za prethodne balanse (u memoriji, resetuje se pri svakom pokretanju)
previous_balances = {}

# 🔄 Dohvati DIS balans za adresu
async def get_dis_balance(address: str) -> float:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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
            r1 = await client.post(RPC_URL, json=payload)
            accounts = r1.json()["result"]["value"]
            if not accounts:
                return 0.0

            token_account = accounts[0]["pubkey"]

            payload_balance = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountBalance",
                "params": [token_account]
            }
            r2 = await client.post(RPC_URL, json=payload_balance)
            return float(r2.json()["result"]["value"]["uiAmount"])
    except Exception as e:
        print(f"[ERROR get_dis_balance] {address}: {e}")
        return 0.0

# 📊 Glavna funkcija – proverava balanse i detektuje promene
async def get_holder_balances_and_activity():
    results = []
    for address in TOP_HOLDERS:
        balance = await get_dis_balance(address)
        old = previous_balances.get(address, balance)
        change = balance - old

        if abs(change) > 10_000:  # prag za "značajnu promenu"
            results.append({
                "address": address,
                "dis_balance": balance,
                "change": change
            })

        # Ažuriraj cache
        previous_balances[address] = balance

    # Vraćamo listu promena i nema "najaktivnijeg" jer ne pratimo tx count
    return results, None
