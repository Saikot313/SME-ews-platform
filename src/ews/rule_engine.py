import json
import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta

DB_PATH = "../../data/sme_ews.db"
RULES_PATH = os.path.join(os.path.dirname(__file__), "rules_config.json")


def get_conn():
    return sqlite3.connect(DB_PATH)


def load_rules():
    with open(RULES_PATH) as f:
        return json.load(f)

def eval_payment_delay(borrower_id, params):
    with get_conn() as conn:
        since = date.today() - timedelta(days=params["lookback_days"])
        df = pd.read_sql(
            f"SELECT * FROM payment_history "
            f"WHERE borrower_id = ? AND due_date >= ?",
            conn, params=(borrower_id, since)
        )
    if df.empty:
        return []

    late = df[df["days_past_due"] >= params["dpd_threshold"]]
    if len(late) >= params["consecutive_occurrences"]:
        return [{
            "borrower_id": borrower_id,
            "signal_date": date.today(),
            "signal_type": "PaymentDelay",
            "signal_value": len(late),
            "severity": "Medium",
            "rule_id": "R001",
        }]
    return []


def eval_transaction_drop(borrower_id, params):
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT txn_date, amount FROM transactions "
            "WHERE borrower_id = ? AND txn_type = 'Credit'",
            conn, params=(borrower_id,)
        )
    if df.empty:
        return []

    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df["month"] = df["txn_date"].dt.to_period("M")
    monthly = df.groupby("month")["amount"].sum().sort_index()

    baseline_months = params["baseline_months"]
    lookback_months = params["lookback_months"]
    if len(monthly) < baseline_months + lookback_months:
        return []

    baseline = monthly.iloc[-(baseline_months + lookback_months):-lookback_months].mean()
    recent = monthly.iloc[-lookback_months:].mean()

    if baseline > 0 and (baseline - recent) / baseline >= params["drop_pct"]:
        return [{
            "borrower_id": borrower_id,
            "signal_date": date.today(),
            "signal_type": "TxnDrop",
            "signal_value": round((baseline - recent) / baseline * 100, 2),
            "severity": "High",
            "rule_id": "R002",
        }]
    return []


def eval_cheque_bounce(borrower_id, params):
    with get_conn() as conn:
        since = date.today() - timedelta(days=params["lookback_months"] * 30)
        df = pd.read_sql(
            "SELECT * FROM transactions "
            "WHERE borrower_id = ? AND category = 'Cheque' AND txn_date >= ?",
            conn, params=(borrower_id, since)
        )
    if len(df) >= params["count_threshold"]:
        return [{
            "borrower_id": borrower_id,
            "signal_date": date.today(),
            "signal_type": "ChequeBounce",
            "signal_value": len(df),
            "severity": "High",
            "rule_id": "R003",
        }]
    return []


def eval_cib_spike(borrower_id, params):
    with get_conn() as conn:
        since = date.today() - timedelta(days=params["lookback_months"] * 30)
        df = pd.read_sql(
            "SELECT * FROM cib_queries "
            "WHERE borrower_id = ? AND query_date >= ?",
            conn, params=(borrower_id, since)
        )
    if df.empty:
        return []

    if (len(df) >= params["query_count"] and
            df["institution_count"].max() >= params["institution_threshold"]):
        return [{
            "borrower_id": borrower_id,
            "signal_date": date.today(),
            "signal_type": "CIBSpike",
            "signal_value": len(df),
            "severity": "Medium",
            "rule_id": "R004",
        }]
    return []


def eval_balance_erosion(borrower_id, params):
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT txn_date, balance_after FROM transactions "
            "WHERE borrower_id = ? ORDER BY txn_date",
            conn, params=(borrower_id,)
        )
    if df.empty:
        return []

    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df["month"] = df["txn_date"].dt.to_period("M")
    monthly_avg = df.groupby("month")["balance_after"].mean().sort_index()

    lookback = params["lookback_months"]
    if len(monthly_avg) < lookback * 2:
        return []

    baseline = monthly_avg.iloc[-lookback * 2:-lookback].mean()
    recent = monthly_avg.iloc[-lookback:].mean()

    if (baseline >= params["min_baseline_balance"] and baseline > 0 and
            (baseline - recent) / baseline >= params["drop_pct"]):
        return [{
            "borrower_id": borrower_id,
            "signal_date": date.today(),
            "signal_type": "BalanceErosion",
            "signal_value": round((baseline - recent) / baseline * 100, 2),
            "severity": "High",
            "rule_id": "R005",
        }]
    return []

RULE_EVALUATORS = {
    "R001": eval_payment_delay,
    "R002": eval_transaction_drop,
    "R003": eval_cheque_bounce,
    "R004": eval_cib_spike,
    "R005": eval_balance_erosion,
}


def evaluate_borrower(borrower_id, rules):
    signals = []
    for rule in rules["rules"]:
        if not rule["enabled"]:
            continue
        evaluator = RULE_EVALUATORS.get(rule["rule_id"])
        if not evaluator:
            continue
        try:
            signals.extend(evaluator(borrower_id, rule["params"]))
        except Exception as e:
            print(f"Rule {rule['rule_id']} failed for {borrower_id}: {e}")
    return signals


def run_all_borrowers():
    rules = load_rules()
    with get_conn() as conn:
        borrowers = pd.read_sql("SELECT borrower_id FROM borrowers", conn)

    all_signals = []
    for bid in borrowers["borrower_id"]:
        all_signals.extend(evaluate_borrower(bid, rules))

    signal_df = pd.DataFrame(all_signals)
    if not signal_df.empty:
        with get_conn() as conn:
            signal_df.to_sql(
                "ews_signals", conn, if_exists="append", index=False
            )
    return signal_df


if __name__ == "__main__":
    df = run_all_borrowers()
    print(f"Total signals detected: {len(df)}")
    if not df.empty:
        print(df.groupby("signal_type").size())