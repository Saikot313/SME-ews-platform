import os
import glob
import pandas as pd

from extract_pdf import parse_pdf
from line_item_mapper import map_dataframe
from ratio_engine import compute_ratios
from benchmark_compare import build_benchmark_table, compare_to_benchmark
from load_to_db import (
    get_conn, load_borrowers, load_financials,
    load_ratios, load_benchmarks
)


PDF_DIR = "../../data/raw/pdf_statements"


def run_full_spreading():
    borrowers = pd.read_csv("../../data/synthetic/borrowers.csv")
    financials = pd.read_csv("../../data/synthetic/financials.csv")

    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    extracted_rows = []
    for pdf_path in pdf_files:
        fname = os.path.basename(pdf_path).replace(".pdf", "")
        borrower_id, fy = fname.split("_")
        df = parse_pdf(pdf_path)
        df["borrower_id"] = borrower_id
        df["fiscal_year"] = int(fy)
        extracted_rows.append(df)

    raw_df = pd.concat(extracted_rows, ignore_index=True)
    print(f"Extracted {len(raw_df)} raw rows from {len(pdf_files)} PDFs")

    mapped = map_dataframe(raw_df)
    mapped["borrower_id"] = raw_df["borrower_id"].values
    mapped["fiscal_year"] = raw_df["fiscal_year"].values
    mapped = mapped.dropna(subset=["standard_line_item"])
    print(f"Mapped {len(mapped)} rows to standard taxonomy")

    all_ratios = []
    for bid in mapped["borrower_id"].unique():
        all_ratios.append(
            compute_ratios(mapped[mapped["borrower_id"] == bid], bid)
        )
    ratios_df = pd.concat(all_ratios, ignore_index=True)
    print(f"Computed {len(ratios_df)} ratio rows")

    bench = build_benchmark_table(ratios_df, borrowers)
    compared = compare_to_benchmark(ratios_df, borrowers, bench)

    os.makedirs("../../data/processed", exist_ok=True)
    mapped.to_csv("../../data/processed/spread_line_items.csv", index=False)
    ratios_df.to_csv("../../data/processed/financial_ratios.csv", index=False)
    compared.to_csv("../../data/processed/ratio_flags.csv", index=False)
    print("Saved to data/processed/")

    return mapped, ratios_df, compared


if __name__ == "__main__":
    run_full_spreading()