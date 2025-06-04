import httpx
import asyncio

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
MONITORED_MINT = "FZ4q...TvojMintOvde"  # Zameni sa tvojim mint tokenom

headers = {"Content-Type": "application/json"}

async def fetch_holder_transactions(address, limit=10):
    async with httpx.AsyncClient() as client:
        # 1. Uzimamo zadnjih X potpisa transakcija za adresu
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": limit}]
        }
        resp = await client.post(SOLANA_RPC_URL, json=payload, headers=headers)
        sig_data = resp.json()

        signatures = [entry["signature"] for entry in sig_data.get("result", [])]

        tx_list = []

        for sig in signatures:
            await asyncio.sleep(0.2)  # da ne preteramo sa zahtevima

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [sig, {"encoding": "jsonParsed"}]
            }
            tx_resp = await client.post(SOLANA_RPC_URL, json=payload, headers=headers)
            tx_data = tx_resp.json().get("result")

            if not tx_data:
                continue

            block_time = tx_data.get("blockTime")
            instructions = tx_data.get("transaction", {}).get("message", {}).get("instructions", [])
            post_token_balances = tx_data.get("meta", {}).get("postTokenBalances", [])
            pre_token_balances = tx_data.get("meta", {}).get("preTokenBalances", [])

            for post in post_token_balances:
                if post.get("mint") != MONITORED_MINT:
                    continue

                owner = post.get("owner")
                decimals = int(post["uiTokenAmount"]["decimals"])
                post_amount = int(post["uiTokenAmount"]["amount"])

                # nađi odgovarajući pre balance
                pre_amount = None
                for pre in pre_token_balances:
                    if pre.get("owner") == owner and pre.get("mint") == MONITORED_MINT:
                        pre_amount = int(pre["uiTokenAmount"]["amount"])
                        break

                if pre_amount is None:
                    continue

                delta_raw = post_amount - pre_amount
                if delta_raw == 0:
                    continue

                token_delta = delta_raw / (10 ** decimals)
                side = "BUY" if delta_raw > 0 else "SELL"

                tx_list.append({
                    "signature": sig,
                    "blockTime": block_time,
                    "owner": owner,
                    "delta": token_delta,
                    "side": side
                })

        return tx_list
