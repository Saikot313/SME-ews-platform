import os
import random
import sqlite3
import pandas as pd
from datetime import date, timedelta

random.seed(42)

DB_PATH = "../../data/sme_ews.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def generate_facilities(borrower_id, stressed=False):
    n_fac = random.randint(1, 3)
    facilities = []
    for i in range(n_fac):
        sanctioned = random.uniform(5_000_000, 50_000_000)
        disbursed = sanctioned * random.uniform(0.7, 1.0)
        outstanding = disbursed * random.uniform(0.4, 0.95)
        status = "NPL" if stressed and random.random() < 0.3 else "Active"

        facilities.append({
            "facility_id": f"FAC{borrower_id[-4:]}{i+1}",
            "borrower_id": borrower_id,
            "facility_type": random.choice(
                ["Term Loan", "Working Capital", "LC", "OD"]
            ),
            "sanctioned_amount": round(sanctioned, 2),
            "disbursed_amount": round(disbursed, 2),
            "outstanding_amount": round(outstanding, 2),
            "interest_rate": round(random.uniform(8.0, 14.0), 2),
            "sanction_date": date.today() - timedelta(days=random.randint(180, 1500)),
            "maturity_date": date.today() + timedelta(days=random.randint(180, 1500)),
            "status": status,
        })
    return facilities


def generate_payments(facility, stressed=False):
    payments = []
    today = date.today()
    n_months = 24
    emi = facility["outstanding_amount"] / n_months

    for m in range(n_months):
        due = today - timedelta(days=(n_months - m) * 30)
        dpd = 0
        status = "OnTime"

        if stressed and m >= n_months - 8:
            r = random.random()
            if r < 0.2:
                dpd = random.randint(30, 90)
                status = "Missed"
            elif r < 0.5:
                dpd = random.randint(16, 45)
                status = "Late"

        paid_date = due + timedelta(days=dpd)
        paid_amount = 0 if status == "Missed" else emi

        payments.append({
            "facility_id": facility["facility_id"],
            "borrower_id": facility["borrower_id"],
            "due_date": due,
            "paid_date": paid_date,
            "due_amount": round(emi, 2),
            "paid_amount": round(paid_amount, 2),
            "days_past_due": dpd,
            "status": status,
        })
    return payments


if __name__ == "__main__":
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")

  
    with get_conn() as conn:
        stressed_df = pd.read_sql(
            "SELECT DISTINCT borrower_id FROM transactions "
            "WHERE category = 'Cheque'", conn
        )
    stressed_ids = set(stressed_df["borrower_id"])

    all_fac = []
    all_pay = []
    for _, b in borrowers.iterrows():
        stressed = b["borrower_id"] in stressed_ids
        facs = generate_facilities(b["borrower_id"], stressed)
        all_fac.extend(facs)
        for f in facs:
            all_pay.extend(generate_payments(f, stressed))

    fac_df = pd.DataFrame(all_fac)
    pay_df = pd.DataFrame(all_pay)

    fac_df.to_csv("../../data/synthetic/loan_facilities.csv", index=False)
    pay_df.to_csv("../../data/synthetic/payment_history.csv", index=False)

    with get_conn() as conn:
        fac_df.to_sql("loan_facilities", conn, if_exists="append", index=False)
        pay_df.to_sql("payment_history", conn, if_exists="append", index=False)

    print(f"Generated {len(fac_df)} facilities, {len(pay_df)} payment records")