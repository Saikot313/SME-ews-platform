import pandas as pd
import numpy as np


BENCHMARK_RATIOS = [
    "Current Ratio", "Quick Ratio", "Debt Equity Ratio",
    "Interest Coverage", "DSCR", "EBITDA Margin",
    "Net Profit Margin", "Return on Assets", "Return on Equity",
]


def build_benchmark_table(ratios_df: pd.DataFrame,
                          borrowers_df: pd.DataFrame):
   
    merged = ratios_df.merge(
        borrowers_df[["borrower_id", "industry"]], on="borrower_id"
    )
    bench = merged.groupby(["industry", "ratio_name"])["ratio_value"].agg(
        p25=lambda x: np.nanpercentile(x.dropna(), 25),
        p50=lambda x: np.nanpercentile(x.dropna(), 50),
        p75=lambda x: np.nanpercentile(x.dropna(), 75),
    ).reset_index()
    return bench


def flag_ratio(ratio_name, value, p25, p50, p75):
    if pd.isna(value):
        return "N/A"

    if ratio_name in ("Debt Equity Ratio",):
        # Lower is better
        if value <= p25:
            return "Good"
        elif value <= p75:
            return "Watch"
        else:
            return "Concern"
    else:
        # Higher is better
        if value >= p75:
            return "Good"
        elif value >= p25:
            return "Watch"
        else:
            return "Concern"


def compare_to_benchmark(ratios_df, borrowers_df, benchmark_df):
    merged = ratios_df.merge(
        borrowers_df[["borrower_id", "industry"]], on="borrower_id"
    ).merge(
        benchmark_df, on=["industry", "ratio_name"], how="left"
    )
    merged["flag"] = merged.apply(
        lambda r: flag_ratio(
            r["ratio_name"], r["ratio_value"],
            r["p25"], r["p50"], r["p75"]
        ), axis=1
    )
    merged["deviation_pct"] = (
        (merged["ratio_value"] - merged["p50"]) / merged["p50"].abs() * 100
    ).round(2)
    return merged


if __name__ == "__main__":
    from ratio_engine import compute_ratios
    fin = pd.read_csv("../../data/synthetic/financials.csv")
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")

    all_ratios = []
    for bid in fin["borrower_id"].unique():
        all_ratios.append(
            compute_ratios(fin[fin["borrower_id"] == bid], bid)
        )
    ratios_df = pd.concat(all_ratios, ignore_index=True)

    bench = build_benchmark_table(ratios_df, borrowers)
    compared = compare_to_benchmark(ratios_df, borrowers, bench)
    print(compared.head(20).to_string())