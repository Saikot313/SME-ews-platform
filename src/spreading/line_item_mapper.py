
import json
import os
import pandas as pd
from rapidfuzz import fuzz, process
from data_generator.config import (
    BALANCE_SHEET_ITEMS,
    INCOME_STATEMENT_ITEMS,
    RAW_LINE_ITEM_VARIANTS
)

STANDARD_ITEMS = BALANCE_SHEET_ITEMS + INCOME_STATEMENT_ITEMS


def build_variant_lookup():
    lookup = {}
    for std_item in STANDARD_ITEMS:
        lookup[std_item.lower()] = std_item
        variants = RAW_LINE_ITEM_VARIANTS.get(std_item, [])
        for v in variants:
            lookup[v.lower()] = std_item
    return lookup


VARIANT_LOOKUP = build_variant_lookup()


def map_line_item(raw_label: str, score_cutoff: int = 80):
    if not raw_label:
        return None, 0

    normalized = raw_label.strip().lower()

    if normalized in VARIANT_LOOKUP:
        return VARIANT_LOOKUP[normalized], 100

    choices = list(VARIANT_LOOKUP.keys())
    best = process.extractOne(
        normalized, choices, scorer=fuzz.token_sort_ratio
    )
    if best and best[1] >= score_cutoff:
        return VARIANT_LOOKUP[best[0]], best[1]

    return None, 0


def map_dataframe(df: pd.DataFrame):
    rows = []
    for _, r in df.iterrows():
        std, conf = map_line_item(r["raw_line_item"])
        rows.append({
            "raw_line_item": r["raw_line_item"],
            "standard_line_item": std,
            "confidence_score": conf,
            "amount": r["amount"],
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from extract_pdf import parse_pdf
    sample = "data/raw/pdf_statements/SME1000_2023.pdf"
    raw_df = parse_pdf(sample)
    mapped = map_dataframe(raw_df)
    print(mapped.to_string())
    unmapped = mapped[mapped["standard_line_item"].isna()]
    print(f"\nUnmapped rows: {len(unmapped)}")
    if len(unmapped) > 0:
        print(unmapped[["raw_line_item"]].to_string())