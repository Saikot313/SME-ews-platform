import os
import random
import sqlite3
import numpy as np
import pandas as pd
from datetime import date, timedelta

from config import INDUSTRIES, NUM_MONTHS_TRANSACTIONS

random.seed(42)
np.random.seed(42)

DB_PATH = "../../data/sme_ews.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def generate_monthly_transactions(borrower_id, industry, stressed=False,
                                   num_months=NUM_MONTHS_TRANSACTIONS):
    
    base_deposit = random.uniform(500_000, 5_000_000)
    base_withdrawal = base_deposit * random.uniform(0.85, 0.98)

    today = date.today()
    start_date = today - timedelta(days=num_months * 30)

    rows = []
    balance = base_deposit * random.uniform(0.5, 1.5)

    for month_idx in range(num_months):
        month_start = start_date + timedelta(days=month_idx * 30)

        if stressed:
            stress_factor = 1.0 - (month_idx / num_months) * 0.6 
        else:
            stress_factor = 1.0 + random.uniform(-0.1, 0.1)

        monthly_deposit = base_deposit * stress_factor
        monthly_withdrawal = base_withdrawal * stress_factor

        n_deposits = random.randint(8, 15)
        for _ in range(n_deposits):
            txn_date = month_start + timedelta(days=random.randint(0, 29))
            amt = monthly_deposit / n_deposits * random.uniform(0.5, 1.5)
            balance += amt
            rows.append({
                "borrower_id": borrower_id,
                "txn_date": txn_date,
                "txn_type": "Credit",
                "amount": round(amt, 2),
                "balance_after": round(balance, 2),
                "narration": random.choice([
                    "Cash Deposit", "RTGS Inward", "NPSB Credit",
                    "Customer Payment", "BEFTN Credit"
                ]),
                "category": "Deposit",
            })

        n_withdrawals = random.randint(10, 20)
        for _ in range(n_withdrawals):
            txn_date = month_start + timedelta(days=random.randint(0, 29))
            amt = monthly_withdrawal / n_withdrawals * random.uniform(0.5, 1.5)
            balance -= amt
            rows.append({
                "borrower_id": borrower_id,
                "txn_date": txn_date,
                "txn_type": "Debit",
                "amount": round(amt, 2),
                "balance_after": round(balance, 2),
                "narration": random.choice([
                    "Supplier Payment", "Salary", "Utility Bill",
                    "Loan EMI", "Cash Withdrawal", "Cheque Payment"
                ]),
                "category": "Withdrawal",
            })

        if stressed and month_idx >= num_months - 4:
            n_bounces = random.randint(1, 2)
            for _ in range(n_bounces):
                txn_date = month_start + timedelta(days=random.randint(0, 29))
                rows.append({
                    "borrower_id": borrower_id,
                    "txn_date": txn_date,
                    "txn_type": "Debit",
                    "amount": 0,
                    "balance_after": round(balance, 2),
                    "narration": "Cheque Returned - Insufficient Fund",
                    "category": "Cheque",
                })

    return pd.DataFrame(rows)


def load_transactions_to_db(txn_df):
    with get_conn() as conn:
        txn_df.to_sql("transactions", conn, if_exists="append", index=False)


if __name__ == "__main__":
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")

    stressed_ids = set(
        random.sample(
            list(borrowers["borrower_id"]),
            k=int(len(borrowers) * 0.30)
        )
    )

    all_txns = []
    for _, b in borrowers.iterrows():
        stressed = b["borrower_id"] in stressed_ids
        df = generate_monthly_transactions(
            b["borrower_id"], b["industry"], stressed=stressed
        )
        all_txns.append(df)

    txn_df = pd.concat(all_txns, ignore_index=True)
    txn_df.to_csv("../../data/synthetic/transactions.csv", index=False)
    load_transactions_to_db(txn_df)

    print(f"Generated {len(txn_df)} transactions for {len(borrowers)} borrowers")
    print(f"Stressed borrowers: {len(stressed_ids)}")