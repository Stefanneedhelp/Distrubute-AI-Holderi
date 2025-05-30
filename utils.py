from collections import Counter

# Prikupi sve transakcije top holdera
all_transactions = []
for holder in holders:
    txs = fetch_holder_transactions(holder, mint, HELIUS_API_KEY, start_time, end_time)
    all_transactions.extend(txs)

if not all_transactions:
    send_telegram_message("📫 Nema aktivnosti holdera")
    return

# Računaj broj transakcija po adresi
address_counts = Counter(tx["owner"] for tx in all_transactions)
most_active_holder, max_count = address_counts.most_common(1)[0]

# Računaj ukupnu vrednost kupovina i prodaja
total_buy = sum(tx["usd_value"] for tx in all_transactions if tx["type"] == "BUY")
total_sell = sum(tx["usd_value"] for tx in all_transactions if tx["type"] == "SELL")
ratio = round(total_buy / total_sell, 2) if total_sell > 0 else "∞"

# Formatiraj poruku
report = f"""📊 Dnevni izveštaj ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')})
Cena: ${token_price:.6f}

Ukupno kupljeno: ${total_buy:,.2f}
Ukupno prodato: ${total_sell:,.2f}
Odnos kupovina/prodaja: {ratio}

🔁 Broj transakcija holdera: {len(all_transactions)}
🔥 Najaktivniji holder: {most_active_holder} ({max_count} transakcije)
"""

send_telegram_message(report)
