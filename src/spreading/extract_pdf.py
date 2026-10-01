
import os
import re
import pdfplumber
import pandas as pd


def extract_tables_from_pdf(pdf_path):
    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    label = (row[0] or "").strip()
                    amount_raw = (row[1] or "").strip()
                    if not label or not amount_raw:
                        continue
                    # Skip header rows
                    if label.lower() in ("particulars", "description", "item"):
                        continue
                    all_rows.append({
                        "raw_line_item": label,
                        "raw_amount": amount_raw,
                    })
    return all_rows


def clean_amount(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    negative = False
    if raw.startswith("(") and raw.endswith(")"):
        negative = True
        raw = raw[1:-1]
    raw = raw.replace(",", "").replace("BDT", "").strip()
    raw = re.sub(r"[^\d.\-]", "", raw)
    try:
        val = float(raw)
        return -val if negative else val
    except ValueError:
        return None


def parse_pdf(pdf_path):
    raw_rows = extract_tables_from_pdf(pdf_path)
    parsed = []
    for r in raw_rows:
        amt = clean_amount(r["raw_amount"])
        if amt is None:
            continue
        parsed.append({
            "raw_line_item": r["raw_line_item"],
            "amount": amt,
        })
    return pd.DataFrame(parsed)


if __name__ == "__main__":
    sample = "../../data/raw/pdf_statements/SME1000_2023.pdf"
    df = parse_pdf(sample)
    print(df.head(20))
    print(f"\nTotal rows extracted: {len(df)}")