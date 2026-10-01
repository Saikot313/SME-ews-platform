import pandas as pd
import numpy as np


HIGHER_IS_BETTER = {
    "Current Ratio", "Quick Ratio", "Interest Coverage", "DSCR",
    "EBITDA Margin", "Net Profit Margin", "Gross Profit Margin",
    "Return on Assets", "Return on Equity", "Asset Turnover",
    "Inventory Turnover",
}

LOWER_IS_BETTER = {
    "Debt Equity Ratio", "Debt to Assets",
    "Receivable Days", "Payable Days", "Working Capital Cycle",
}


def compute_trends(ratios_df: pd.DataFrame):
    out = []
    for (bid, ratio), grp in ratios_df.groupby(
        ["borrower_id", "ratio_name"]
    ):
        grp = grp.sort_values("fiscal_year")
        vals = grp["ratio_value"].tolist()
        years = grp["fiscal_year"].tolist()

        if len(vals) < 2:
            continue

        for i in range(1, len(vals)):
            prev, curr = vals[i - 1], vals[i]
            if prev is None or curr is None or prev == 0:
                change_pct = None
                direction = "N/A"
            else:
                change_pct = ((curr - prev) / abs(prev)) * 100
                if ratio in HIGHER_IS_BETTER:
                    direction = "Improving" if curr > prev else "Deteriorating"
                elif ratio in LOWER_IS_BETTER:
                    direction = "Improving" if curr < prev else "Deteriorating"
                else:
                    direction = "Stable"

            out.append({
                "borrower_id": bid,
                "ratio_name": ratio,
                "from_year": years[i - 1],
                "to_year": years[i],
                "from_value": prev,
                "to_value": curr,
                "change_pct": round(change_pct, 2) if change_pct else None,
                "direction": direction,
            })

    return pd.DataFrame(out)


if __name__ == "__main__":
    from ratio_engine import compute_ratios
    fin = pd.read_csv("../../data/synthetic/financials.csv")
    bid = fin["borrower_id"].iloc[0]
    ratios = compute_ratios(fin[fin["borrower_id"] == bid], bid)
    trends = compute_trends(ratios)
    print(trends.to_string())