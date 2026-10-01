import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), "..", "src", "spreading"
))

from extract_pdf import clean_amount
from line_item_mapper import map_line_item


def test_clean_amount_basic():
    assert clean_amount("1,234,567.89") == 1234567.89
    assert clean_amount("  5000  ") == 5000.0
    assert clean_amount("(1,000)") == -1000.0
    assert clean_amount("BDT 500,000") == 500000.0
    print("✓ test_clean_amount_basic passed")


def test_clean_amount_invalid():
    assert clean_amount("") is None
    assert clean_amount("ABC") is None
    assert clean_amount(None) is None
    print("✓ test_clean_amount_invalid passed")


def test_map_line_item_exact():
    std, conf = map_line_item("Cash and Cash Equivalents")
    assert std == "Cash & Cash Equivalents"
    assert conf == 100
    print("✓ test_map_line_item_exact passed")


def test_map_line_item_fuzzy():
    std, conf = map_line_item("Trade Receivables")
    assert std == "Accounts Receivable"
    assert conf >= 80
    print("✓ test_map_line_item_fuzzy passed")


def test_map_line_item_unknown():
    std, conf = map_line_item("Random Garbage Line Item 12345")
    assert std is None
    assert conf == 0
    print("✓ test_map_line_item_unknown passed")


if __name__ == "__main__":
    test_clean_amount_basic()
    test_clean_amount_invalid()
    test_map_line_item_exact()
    test_map_line_item_fuzzy()
    test_map_line_item_unknown()
    print("\nAll extraction tests passed.")