
import pandas as pd
import numpy as np


def _get(df, item, year):
    
    match = df[
        (df["standard_line_item"] == item) &
        (df["fiscal_year"] == year)
    ]
    if match.empty:
        return np.nan
    return match["amount"].iloc[0]


def compute_ratios(mapped_df: pd.DataFrame, borrower_id: str):
    years = sorted(mapped_df["fiscal_year"].unique())
    results = []

    for year in years:
        y_df = mapped_df[mapped_df["fiscal_year"] == year]

        revenue = _get(y_df, "Revenue", year)
        cogs = _get(y_df, "Cost of Goods Sold", year)
        ebitda = _get(y_df, "EBITDA", year)
        ebit = _get(y_df, "EBIT", year)
        interest = _get(y_df, "Interest Expense", year)
        net_profit = _get(y_df, "Net Profit", year)

        ca = (
            _get(y_df, "Cash & Cash Equivalents", year)
            + _get(y_df, "Accounts Receivable", year)
            + _get(y_df, "Inventory", year)
            + _get(y_df, "Other Current Assets", year)
        )
        cl = (
            _get(y_df, "Short Term Loan", year)
            + _get(y_df, "Accounts Payable", year)
            + _get(y_df, "Other Current Liabilities", year)
        )
        inventory = _get(y_df, "Inventory", year)
        ar = _get(y_df, "Accounts Receivable", year)
        ap = _get(y_df, "Accounts Payable", year)
        total_debt = (
            _get(y_df, "Short Term Loan", year)
            + _get(y_df, "Long Term Loan", year)
        )
        total_equity = _get(y_df, "Total Equity", year)
        total_assets = _get(y_df, "Total Assets", year)

        ratios = {
            "Current Ratio": ca / cl if cl else np.nan,
            "Quick Ratio": (ca - inventory) / cl if cl else np.nan,
            "Debt Equity Ratio": total_debt / total_equity if total_equity else np.nan,
            "Debt to Assets": total_debt / total_assets if total_assets else np.nan,
            "Interest Coverage": ebit / interest if interest else np.nan,
            "DSCR": ebitda / interest if interest else np.nan,
            "EBITDA Margin": ebitda / revenue if revenue else np.nan,
            "Net Profit Margin": net_profit / revenue if revenue else np.nan,
            "Gross Profit Margin": (revenue - cogs) / revenue if revenue else np.nan,
            "Return on Assets": net_profit / total_assets if total_assets else np.nan,
            "Return on Equity": net_profit / total_equity if total_equity else np.nan,
            "Asset Turnover": revenue / total_assets if total_assets else np.nan,
            "Inventory Turnover": cogs / inventory if inventory else np.nan,
            "Receivable Days": (ar / revenue) * 365 if revenue else np.nan,
            "Payable Days": (ap / cogs) * 365 if cogs else np.nan,
            "Working Capital Cycle": (
                ((ar / revenue) * 365 if revenue else 0)
                + ((inventory / cogs) * 365 if cogs else 0)
                - ((ap / cogs) * 365 if cogs else 0)
            ),
        }

        for name, val in ratios.items():
            results.append({
                "borrower_id": borrower_id,
                "fiscal_year": year,
                "ratio_name": name,
                "ratio_value": round(float(val), 4) if pd.notna(val) else None,
            })

    return pd.DataFrame(results)


if __name__ == "__main__":
    fin = pd.read_csv("../../data/synthetic/financials.csv")
    sample_bid = fin["borrower_id"].iloc[0]
    sample = fin[fin["borrower_id"] == sample_bid].copy()
    sample["standard_line_item"] = sample["standard_line_item"]
    ratios = compute_ratios(sample, sample_bid)
    print(ratios.to_string())