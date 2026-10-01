import os
import sqlite3
import pandas as pd

DB_PATH = "../../data/sme_ews.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def load_borrowers():
    df = pd.read_csv("../../data/synthetic/borrowers.csv")
    with get_conn() as conn:
        df.to_sql("borrowers", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} borrowers")


def load_financials():
    df = pd.read_csv("../../data/synthetic/financials.csv")
    df.insert(0, "statement_id", range(1, len(df) + 1))
    df.rename(columns={"standard_line_item": "standard_line_item"}, inplace=True)
    df["statement_category"] = df["statement_category"]
    df["raw_line_item"] = df["standard_line_item"]
    df["confidence_score"] = 100
    with get_conn() as conn:
        df[[
            "statement_id", "borrower_id", "fiscal_year",
            "statement_category", "standard_line_item",
            "raw_line_item", "amount", "confidence_score"
        ]].to_sql(
            "spread_line_items", conn, if_exists="append", index=False
        )
    print(f"Loaded {len(df)} spread line items")


def load_ratios(ratios_df):
    with get_conn() as conn:
        ratios_df.to_sql(
            "financial_ratios", conn, if_exists="append", index=False
        )
    print(f"Loaded {len(ratios_df)} ratio rows")


def load_benchmarks(bench_df):
    bench_df = bench_df.rename(columns={
        "p25": "p25_value", "p50": "p50_value", "p75": "p75_value"
    })
    bench_df["ratio_name"] = bench_df["ratio_name"]
    with get_conn() as conn:
        bench_df.to_sql(
            "industry_benchmark", conn, if_exists="append", index=False
        )
    print(f"Loaded {len(bench_df)} benchmark rows")


if __name__ == "__main__":
    from ratio_engine import compute_ratios
    from benchmark_compare import build_benchmark_table

    load_borrowers()
    load_financials()

    fin = pd.read_csv("../../data/synthetic/financials.csv")
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")

    all_ratios = []
    for bid in fin["borrower_id"].unique():
        all_ratios.append(
            compute_ratios(fin[fin["borrower_id"] == bid], bid)
        )
    ratios_df = pd.concat(all_ratios, ignore_index=True)
    load_ratios(ratios_df)

    bench = build_benchmark_table(ratios_df, borrowers)
    load_benchmarks(bench)

    print("\nAll data loaded to SQLite.")