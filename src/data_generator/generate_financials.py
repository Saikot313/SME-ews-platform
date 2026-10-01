import random
import pandas as pd
from config import (
    INDUSTRIES, BALANCE_SHEET_ITEMS, INCOME_STATEMENT_ITEMS,
    NUM_YEARS_FINANCIAL
)

random.seed(42)


def generate_financials_for_borrower(borrower):
    industry = borrower["industry"]
    cfg = INDUSTRIES[industry]

    revenue_base = random.uniform(*cfg["revenue_range"])
    asset_base = random.uniform(*cfg["asset_range"])
    de_ratio = random.uniform(*cfg["debt_equity_range"])
    current_ratio = random.uniform(*cfg["current_ratio_range"])
    dscr = random.uniform(*cfg["dscr_range"])

    rows = []
    for year_offset in range(NUM_YEARS_FINANCIAL):
        fiscal_year = 2023 - year_offset
        growth = random.uniform(-0.05, 0.15)  # yearly growth
        revenue = revenue_base * (1 + growth) ** (NUM_YEARS_FINANCIAL - year_offset)

        cogs = revenue * random.uniform(0.60, 0.75)
        gross_profit = revenue - cogs
        opex = gross_profit * random.uniform(0.30, 0.50)
        ebitda = gross_profit - opex
        depreciation = asset_base * random.uniform(0.05, 0.10)
        ebit = ebitda - depreciation
        interest_expense = ebitda / dscr if dscr > 0 else 0
        pbt = ebit - interest_expense
        tax = max(pbt * 0.25, 0)
        net_profit = pbt - tax

        total_equity = asset_base / (1 + de_ratio)
        total_liabilities = asset_base - total_equity
        short_term_loan = total_liabilities * random.uniform(0.4, 0.6)
        long_term_loan = total_liabilities - short_term_loan

        current_assets = short_term_loan * current_ratio
        cash = current_assets * random.uniform(0.10, 0.25)
        ar = current_assets * random.uniform(0.35, 0.50)
        inventory = current_assets - cash - ar
        other_current_assets = current_assets * 0.05

        net_fixed_assets = asset_base - current_assets
        accounts_payable = current_assets * random.uniform(0.30, 0.50)
        other_current_liab = current_assets * 0.10

        is_data = {
            "Revenue": revenue,
            "Cost of Goods Sold": cogs,
            "Gross Profit": gross_profit,
            "Operating Expenses": opex,
            "EBITDA": ebitda,
            "Depreciation": depreciation,
            "EBIT": ebit,
            "Interest Expense": interest_expense,
            "Profit Before Tax": pbt,
            "Tax": tax,
            "Net Profit": net_profit,
        }
        bs_data = {
            "Cash & Cash Equivalents": cash,
            "Accounts Receivable": ar,
            "Inventory": inventory,
            "Other Current Assets": other_current_assets,
            "Net Fixed Assets": net_fixed_assets,
            "Total Assets": asset_base,
            "Short Term Loan": short_term_loan,
            "Accounts Payable": accounts_payable,
            "Other Current Liabilities": other_current_liab,
            "Long Term Loan": long_term_loan,
            "Total Liabilities": total_liabilities,
            "Share Capital": total_equity * 0.4,
            "Retained Earnings": total_equity * 0.6,
            "Total Equity": total_equity,
        }

        for item, amt in is_data.items():
            rows.append({
                "borrower_id": borrower["borrower_id"],
                "fiscal_year": fiscal_year,
                "statement_category": "IncomeStatement",
                "standard_line_item": item,
                "amount": round(amt, 2),
            })
        for item, amt in bs_data.items():
            rows.append({
                "borrower_id": borrower["borrower_id"],
                "fiscal_year": fiscal_year,
                "statement_category": "BalanceSheet",
                "standard_line_item": item,
                "amount": round(amt, 2),
            })

    return rows


if __name__ == "__main__":
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")
    all_rows = []
    for _, b in borrowers.iterrows():
        all_rows.extend(generate_financials_for_borrower(b))

    df = pd.DataFrame(all_rows)
    df.to_csv("../../data/synthetic/financials.csv", index=False)
    print(f"Generated {len(df)} financial line items for {len(borrowers)} borrowers")
    print(df.head())