import httpx
import os
import asyncio
from datetime import datetime, timedelta
from utils import get_token_price

RPC_URL = os.getenv("RPC_URL")
POOL_ADDRESS = "AyCkqVaYArj6uGvVhEqKUw6vY2BrZhS1F13ArLTVaCKn"
DIS_MINT = os.getenv("DIS_MINT")

async def get_recent_swaps():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Dohvati transakcije za Meteora pool
            sig_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [POOL_ADDRESS, {"limit": 50}]
            }
            sig_resp = await client.post(RPC_URL, json=sig_payload)
            sigs = sig_resp.json()["result"]

            now = datetime.utcnow()
            dis_in = 0
            dis_out = 0

            for sig in sigs:
                sig_str = sig["signature"]
                block_time = sig.get("blockTime")
                if not block_time:
                    continue
                tx_time = datetime.utcfromtimestamp(block_time)
                if now - tx_time > timedelta(hours=24):
                    continue

                # 2. Dohvati detalje transakcije
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [sig_str, {"encoding": "jsonParsed"}]
                }
                tx_resp = await client.post(RPC_URL, json=tx_payload)
                tx = tx_resp.json().get("result")
                if not tx:
                    continue

                # 3. Traži tokene u swapovima
                instructions = tx["transaction"]["message"]["instructions"]
                for ix in instructions:
                    if "parsed" in ix and ix["parsed"]["type"] == "transfer":
                        info = ix["parsed"]["info"]
                        mint = info.get("mint")
                        amount = float(info.get("amount", 0)) / 1_000_000  # DIS ima 6 decimala
                        if mint == DIS_MINT:
                            source = info["source"]
                            dest = info["destination"]
                            if source == POOL_ADDRESS:
                                dis_out += amount  # neko je kupio DIS
                            elif dest == POOL_ADDRESS:
                                dis_in += amount   # neko je prodao DIS

            return dis_in, dis_out

    except Exception as e:
        print(f"[ERROR get_recent_swaps] {e}")
        return 0.0, 0.0

async def main():
    dis_in, dis_out = await get_recent_swaps()
    price = await get_token_price()
    msg = "📊 DIS Swap izveštaj (24h, Meteora)\n"
    msg += f"💵 Cena (Jupiter): ${price:.6f}\n"
    msg += f"🟢 Kupovine: {dis_out:,.1f} DIS = ${dis_out * price:,.0f}\n"
    msg += f"🔴 Prodaje: {dis_in:,.1f} DIS = ${dis_in * price:,.0f}\n"
    print(msg)

if __name__ == "__main__":
    asyncio.run(main())
