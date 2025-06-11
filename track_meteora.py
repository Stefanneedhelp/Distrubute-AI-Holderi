
import httpx
import os
import asyncio
from utils import get_token_price

RPC_URL = os.getenv("RPC_URL")
DIS_MINT = os.getenv("DIS_MINT")
POOL_OWNER = "AyCkqVaYArj6uGvVhEqKUw6vY2BrZhS1F13ArLTVaCKn"  # Meteora pool address
POOL_TOKEN_ACCOUNT = None  # popuni ako veÄ‡ znaÅ¡ ruÄno

async def get_token_account_for_pool():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    POOL_OWNER,
                    {"mint": DIS_MINT},
                    {"encoding": "jsonParsed"}
                ]
            }
            r = await client.post(RPC_URL, json=payload)
            result = r.json()["result"]["value"]
            if not result:
                return None
            return result[0]["pubkey"]
    except Exception as e:
        print(f"[ERROR get_token_account_for_pool] {e}")
        return None

async def get_dis_balance(account_address: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountBalance",
                "params": [account_address]
            }
            r = await client.post(RPC_URL, json=payload)
            balance = r.json()["result"]["value"]["uiAmount"]
            return float(balance)
    except Exception as e:
        print(f"[ERROR get_dis_balance] {e}")
        return 0.0

async def get_recent_swaps_by_balance():
    try:
        token_account = POOL_TOKEN_ACCOUNT or await get_token_account_for_pool()
        if not token_account:
            print("[ERROR] DIS token account za pool nije pronaÄ‘en.")
            return 0.0, 0.0

        current_balance = await get_dis_balance(token_account)

        try:
            with open("prev_balance.txt", "r") as f:
                prev_balance = float(f.read())
        except:
            prev_balance = current_balance

        delta = current_balance - prev_balance
        dis_in = abs(delta) if delta > 0 else 0.0
        dis_out = abs(delta) if delta < 0 else 0.0

        with open("prev_balance.txt", "w") as f:
            f.write(str(current_balance))

        return dis_in, dis_out

    except Exception as e:
        print(f"[ERROR get_recent_swaps_by_balance] {e}")
        return 0.0, 0.0

async def main():
    dis_in, dis_out = await get_recent_swaps_by_balance()
    price = await get_token_price()
    print("ðŸ“Š DIS Pool Analiza (Meteora)")
    print(f"ðŸ’µ Cena: ${price:.6f}")
    print(f"ðŸŸ¢ Kupovine: {dis_out:,.1f} DIS = ${dis_out * price:,.0f}")
    print(f"ðŸ”´ Prodaje: {dis_in:,.1f} DIS = ${dis_in * price:,.0f}")

if __name__ == "__main__":
    asyncio.run(main())
