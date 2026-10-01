import random
import sqlite3
import pandas as pd
from datetime import date, timedelta

random.seed(42)
DB_PATH = "../../data/sme_ews.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


if __name__ == "__main__":
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")

    with get_conn() as conn:
        stressed_df = pd.read_sql(
            "SELECT DISTINCT borrower_id FROM transactions "
            "WHERE category = 'Cheque'", conn
        )
    stressed_ids = set(stressed_df["borrower_id"])

    rows = []
    today = date.today()
    for _, b in borrowers.iterrows():
        stressed = b["borrower_id"] in stressed_ids
        n_queries = random.randint(6, 12) if stressed else random.randint(0, 3)

        for _ in range(n_queries):
            q_date = today - timedelta(days=random.randint(0, 90))
            rows.append({
                "borrower_id": b["borrower_id"],
                "query_date": q_date,
                "query_purpose": random.choice(
                    ["New Facility", "Renewal", "Enhancement", "Annual Review"]
                ),
                "institution_count": random.randint(1, 5) if stressed else 1,
            })

    df = pd.DataFrame(rows)
    df.to_csv("../../data/synthetic/cib_queries.csv", index=False)
    with get_conn() as conn:
        df.to_sql("cib_queries", conn, if_exists="append", index=False)

    print(f"Generated {len(df)} CIB query records")