
import json
import sqlite3
import os
import pandas as pd
import numpy as np
from datetime import date, timedelta

DB_PATH = "../../data/sme_ews.db"
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules_config.json")


def get_conn():
    return sqlite3.connect(DB_PATH)


def load_config():
    with open(RULES_PATH) as f:
        return json.load(f)


def weight_for_signal(signal_type, rules):
    for r in rules["rules"]:
        if r["signal_type"] == signal_type:
            return r["weight"]
    return 0


def compute_score(borrower_id, rules):
    with get_conn() as conn:
        since = date.today() - timedelta(days=90)
        df = pd.read_sql(
            "SELECT * FROM ews_signals "
            "WHERE borrower_id = ? AND signal_date >= ?",
            conn, params=(borrower_id, since)
        )
    if df.empty:
        return 0, 0

    total = 0
    seen_types = set()
    for _, r in df.iterrows():
        if r["signal_type"] in seen_types:
            continue
        seen_types.add(r["signal_type"])
        total += weight_for_signal(r["signal_type"], rules)

    return min(total, 100), len(df)


def classify(score, thresholds):
    for zone, (lo, hi) in thresholds.items():
        if lo <= score <= hi:
            return zone
    return "Red" 


def run_classification():
    rules = load_config()
    thresholds = rules["zone_thresholds"]

    with get_conn() as conn:
        borrowers = pd.read_sql("SELECT borrower_id FROM borrowers", conn)

    results = []
    for bid in borrowers["borrower_id"]:
        score, n_signals = compute_score(bid, rules)
        zone = classify(score, thresholds)
        results.append({
            "borrower_id": bid,
            "as_of_date": date.today(),
            "zone": zone,
            "total_score": score,
            "active_signals": n_signals,
        })

    df = pd.DataFrame(results)

    with get_conn() as conn:
        prev = pd.read_sql(
            "SELECT borrower_id, zone FROM borrower_zones "
            "WHERE as_of_date = (SELECT MAX(as_of_date) FROM borrower_zones)",
            conn
        )
    prev_map = dict(zip(prev["borrower_id"], prev["zone"]))
    df["previous_zone"] = df["borrower_id"].map(prev_map)
    df["zone_changed_date"] = df.apply(
        lambda r: date.today() if r["zone"] != r.get("previous_zone") else None,
        axis=1
    )

    with get_conn() as conn:
        df.to_sql("borrower_zones", conn, if_exists="append", index=False)

    return df


if __name__ == "__main__":
    df = run_classification()
    print(df.groupby("zone").size())
    print(df.head(10).to_string())