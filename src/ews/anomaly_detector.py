
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "../../data/sme_ews.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def detect_anomalies(borrower_id, window=30, z_threshold=2.5):
    
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT txn_date, amount, txn_type FROM transactions "
            "WHERE borrower_id = ? ORDER BY txn_date",
            conn, params=(borrower_id,)
        )
    if df.empty:
        return pd.DataFrame()

    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df["signed_amount"] = np.where(
        df["txn_type"] == "Credit", df["amount"], -df["amount"]
    )
    daily = df.groupby("txn_date")["signed_amount"].sum().sort_index()

    rolling_mean = daily.rolling(window=window, min_periods=10).mean()
    rolling_std = daily.rolling(window=window, min_periods=10).std()
    z = (daily - rolling_mean) / rolling_std.replace(0, np.nan)

    anomalies = daily[z.abs() > z_threshold]
    out = pd.DataFrame({
        "borrower_id": borrower_id,
        "anomaly_date": anomalies.index,
        "daily_net": anomalies.values,
        "z_score": z.loc[anomalies.index].round(2).values,
    })
    return out


if __name__ == "__main__":
    with get_conn() as conn:
        borrowers = pd.read_sql(
            "SELECT borrower_id FROM borrowers LIMIT 5", conn
        )
    for bid in borrowers["borrower_id"]:
        res = detect_anomalies(bid)
        print(f"{bid}: {len(res)} anomalies")