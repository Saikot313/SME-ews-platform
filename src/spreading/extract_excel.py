
import pandas as pd
from extract_pdf import clean_amount


def parse_excel(xlsx_path, sheet_name=0):
    
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None)
    parsed = []
    for _, row in df.iterrows():
        if len(row) < 2:
            continue
        label = str(row[0]).strip()
        amt_raw = row[1]
        if not label or label.lower() in ("nan", "particulars", "description"):
            continue
        if isinstance(amt_raw, str):
            amt = clean_amount(amt_raw)
        else:
            try:
                amt = float(amt_raw)
            except (ValueError, TypeError):
                amt = None
        if amt is None:
            continue
        parsed.append({
            "raw_line_item": label,
            "amount": amt,
        })
    return pd.DataFrame(parsed)


if __name__ == "__main__":
    print("Excel parser ready. Provide xlsx_path to test.")