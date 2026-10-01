
import os
import random
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from config import RAW_LINE_ITEM_VARIANTS

random.seed(42)

OUTPUT_DIR = "../../data/raw/pdf_statements"
os.makedirs(OUTPUT_DIR, exist_ok=True)

STYLES = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle(
    "TitleStyle", parent=STYLES["Heading1"],
    fontSize=14, alignment=1, spaceAfter=10
)
SUB_STYLE = ParagraphStyle(
    "SubStyle", parent=STYLES["Normal"],
    fontSize=10, alignment=1, spaceAfter=6
)


def get_raw_label(standard_item: str) -> str:
    """Return a random raw variant for a standard line item."""
    variants = RAW_LINE_ITEM_VARIANTS.get(standard_item)
    if variants:
        return random.choice(variants)
    return standard_item


def build_table(rows, header):
    """Build a reportlab table with a header."""
    data = [header] + rows
    table = Table(data, colWidths=[280, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F4F6F7")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def generate_pdf_for_borrower(borrower_id, borrower_name, industry,
                              fiscal_year, fin_df, layout_variant=0):
    """
    Generate a single PDF for one borrower-year.
    layout_variant: 0 = BalanceSheet first, 1 = IncomeStatement first,
                    2 = Combined single table
    """
    file_path = os.path.join(
        OUTPUT_DIR, f"{borrower_id}_{fiscal_year}.pdf"
    )
    doc = SimpleDocTemplate(
        file_path, pagesize=A4,
        topMargin=30, bottomMargin=30,
        leftMargin=40, rightMargin=40
    )
    elements = []

    # ---- Header ----
    elements.append(Paragraph(borrower_name, TITLE_STYLE))
    elements.append(Paragraph(
        f"{industry} | Financial Statements | FY {fiscal_year}",
        SUB_STYLE
    ))
    elements.append(Spacer(1, 12))

    bs_df = fin_df[
        (fin_df["fiscal_year"] == fiscal_year) &
        (fin_df["statement_category"] == "BalanceSheet")
    ]
    is_df = fin_df[
        (fin_df["fiscal_year"] == fiscal_year) &
        (fin_df["statement_category"] == "IncomeStatement")
    ]

    def build_rows(df):
        rows = []
        for _, r in df.iterrows():
            raw_label = get_raw_label(r["standard_line_item"])
            amount = f"{r['amount']:,.2f}"
            rows.append([raw_label, amount])
        return rows

    if layout_variant == 0:
        elements.append(Paragraph("Balance Sheet", STYLES["Heading2"]))
        elements.append(build_table(
            build_rows(bs_df), ["Particulars", "Amount (BDT)"]
        ))
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("Income Statement", STYLES["Heading2"]))
        elements.append(build_table(
            build_rows(is_df), ["Particulars", "Amount (BDT)"]
        ))

    elif layout_variant == 1:
        elements.append(Paragraph("Income Statement", STYLES["Heading2"]))
        elements.append(build_table(
            build_rows(is_df), ["Particulars", "Amount (BDT)"]
        ))
        elements.append(Spacer(1, 14))
        elements.append(Paragraph("Balance Sheet", STYLES["Heading2"]))
        elements.append(build_table(
            build_rows(bs_df), ["Particulars", "Amount (BDT)"]
        ))

    else:  # variant 2: combined
        combined = pd.concat([is_df, bs_df], ignore_index=True)
        elements.append(Paragraph("Financial Statements", STYLES["Heading2"]))
        elements.append(build_table(
            build_rows(combined), ["Particulars", "Amount (BDT)"]
        ))

    doc.build(elements)
    return file_path


if __name__ == "__main__":
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")
    financials = pd.read_csv("../../data/synthetic/financials.csv")

    count = 0
    for _, b in borrowers.iterrows():
        for fy in financials[
            financials["borrower_id"] == b["borrower_id"]
        ]["fiscal_year"].unique():
            variant = random.choice([0, 1, 2])
            generate_pdf_for_borrower(
                b["borrower_id"], b["borrower_name"],
                b["industry"], fy, financials, variant
            )
            count += 1

    print(f"Generated {count} synthetic PDF statements in {OUTPUT_DIR}")