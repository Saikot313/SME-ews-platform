
INDUSTRIES = {
    "RMG": {
        "sub_industries": ["Knitwear", "Woven", "Garments Accessories"],
        "revenue_range": (50_000_000, 500_000_000),      # BDT
        "asset_range": (30_000_000, 300_000_000),
        "debt_equity_range": (0.8, 2.5),
        "current_ratio_range": (1.0, 1.8),
        "dscr_range": (1.1, 2.2),
        "default_prob": 0.12,
    },
    "Textile": {
        "sub_industries": ["Spinning", "Dyeing", "Finishing"],
        "revenue_range": (80_000_000, 800_000_000),
        "asset_range": (50_000_000, 500_000_000),
        "debt_equity_range": (1.0, 2.8),
        "current_ratio_range": (1.0, 1.6),
        "dscr_range": (1.0, 2.0),
        "default_prob": 0.15,
    },
    "Food & Beverage": {
        "sub_industries": ["Processed Food", "Beverage", "Agro"],
        "revenue_range": (20_000_000, 200_000_000),
        "asset_range": (15_000_000, 150_000_000),
        "debt_equity_range": (0.5, 1.8),
        "current_ratio_range": (1.2, 2.2),
        "dscr_range": (1.3, 2.5),
        "default_prob": 0.08,
    },
    "Pharmaceutical": {
        "sub_industries": ["Formulation", "API", "Packaging"],
        "revenue_range": (100_000_000, 1_000_000_000),
        "asset_range": (80_000_000, 700_000_000),
        "debt_equity_range": (0.3, 1.2),
        "current_ratio_range": (1.5, 2.8),
        "dscr_range": (1.5, 3.0),
        "default_prob": 0.05,
    },
    "Trading": {
        "sub_industries": ["Import", "Export", "Distribution"],
        "revenue_range": (30_000_000, 300_000_000),
        "asset_range": (10_000_000, 100_000_000),
        "debt_equity_range": (1.5, 4.0),
        "current_ratio_range": (1.0, 1.5),
        "dscr_range": (1.0, 1.8),
        "default_prob": 0.18,
    },
    "Light Engineering": {
        "sub_industries": ["Fabrication", "Machinery", "Electrical"],
        "revenue_range": (15_000_000, 150_000_000),
        "asset_range": (10_000_000, 100_000_000),
        "debt_equity_range": (0.8, 2.2),
        "current_ratio_range": (1.1, 1.9),
        "dscr_range": (1.1, 2.0),
        "default_prob": 0.14,
    },
}

DISTRICTS = ["Dhaka", "Chattogram", "Narayanganj", "Gazipur", "Khulna", "Sylhet", "Bogura"]

LEGAL_STRUCTURES = ["Sole Proprietorship", "Partnership", "Private Limited", "Public Limited"]

BALANCE_SHEET_ITEMS = [
    "Cash & Cash Equivalents",
    "Accounts Receivable",
    "Inventory",
    "Other Current Assets",
    "Net Fixed Assets",
    "Total Assets",
    "Short Term Loan",
    "Accounts Payable",
    "Other Current Liabilities",
    "Long Term Loan",
    "Total Liabilities",
    "Share Capital",
    "Retained Earnings",
    "Total Equity",
]

INCOME_STATEMENT_ITEMS = [
    "Revenue",
    "Cost of Goods Sold",
    "Gross Profit",
    "Operating Expenses",
    "EBITDA",
    "Depreciation",
    "EBIT",
    "Interest Expense",
    "Profit Before Tax",
    "Tax",
    "Net Profit",
]

RAW_LINE_ITEM_VARIANTS = {
    "Cash & Cash Equivalents": [
        "Cash and Cash Equivalents", "Cash & Bank Balance", "Cash and Bank",
        "Cash in Hand and at Bank", "Cash & Cash Equivalent"
    ],
    "Accounts Receivable": [
        "Trade Receivables", "Accounts Receivable", "Debtors",
        "Sundry Debtors", "Receivables"
    ],
    "Inventory": [
        "Inventories", "Stock in Trade", "Inventory", "Stock",
        "Closing Stock"
    ],
    "Net Fixed Assets": [
        "Property Plant & Equipment", "Fixed Assets", "Net Block",
        "Tangible Assets", "PP&E"
    ],
    "Revenue": [
        "Sales", "Turnover", "Revenue", "Net Sales", "Total Revenue"
    ],
    "Cost of Goods Sold": [
        "COGS", "Cost of Sales", "Cost of Goods Sold", "Direct Cost"
    ],
}

RATIO_FLAGS = {
    "DSCR": {"good": 1.5, "watch": 1.2, "concern": 1.0},
    "Current Ratio": {"good": 1.5, "watch": 1.2, "concern": 1.0},
    "Debt Equity": {"good": 1.5, "watch": 2.5, "concern": 3.5},  # inverse
    "Interest Coverage": {"good": 3.0, "watch": 2.0, "concern": 1.5},
    "EBITDA Margin": {"good": 0.15, "watch": 0.08, "concern": 0.05},
}

EWS_RULES = {
    "payment_delay": {
        "threshold_dpd": 15,
        "severity": "Medium",
        "weight": 20,
    },
    "transaction_drop": {
        "drop_pct": 0.40,          
        "lookback_months": 3,
        "severity": "High",
        "weight": 25,
    },
    "cheque_bounce": {
        "count_threshold": 2,
        "lookback_months": 6,
        "severity": "High",
        "weight": 25,
    },
    "cib_spike": {
        "query_count": 5,
        "lookback_months": 3,
        "severity": "Medium",
        "weight": 15,
    },
    "balance_erosion": {
        "drop_pct": 0.50,
        "lookback_months": 3,
        "severity": "High",
        "weight": 20,
    },
}

ZONE_THRESHOLDS = {
    "Green": (0, 30),
    "Amber": (31, 60),
    "Red": (61, 100),
}

NUM_BORROWERS = 120
NUM_YEARS_FINANCIAL = 3
NUM_MONTHS_TRANSACTIONS = 24
NUM_FACILITIES_PER_BORROWER = (1, 3)