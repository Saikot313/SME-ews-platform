
import random
import sqlite3
import pandas as pd
from datetime import date, timedelta
from faker import Faker
from config import INDUSTRIES, DISTRICTS, LEGAL_STRUCTURES, NUM_BORROWERS

fake = Faker("en_BD")
random.seed(42)


def generate_borrowers():
    borrowers = []
    for i in range(NUM_BORROWERS):
        industry = random.choice(list(INDUSTRIES.keys()))
        sub_industry = random.choice(INDUSTRIES[industry]["sub_industries"])

        incorporation_date = fake.date_between(
            start_date="-20y", end_date="-2y"
        )
        onboarding_date = fake.date_between(
            start_date="-5y", end_date="today"
        )

        borrower = {
            "borrower_id": f"SME{1000 + i}",
            "borrower_name": fake.company(),
            "industry": industry,
            "sub_industry": sub_industry,
            "incorporation_date": incorporation_date,
            "legal_structure": random.choice(LEGAL_STRUCTURES),
            "district": random.choice(DISTRICTS),
            "relationship_manager": fake.name(),
            "onboarding_date": onboarding_date,
        }
        borrowers.append(borrower)

    return pd.DataFrame(borrowers)


if __name__ == "__main__":
    df = generate_borrowers()
    df.to_csv("../../data/synthetic/borrowers.csv", index=False)
    print(f"Generated {len(df)} borrowers")
    print(df.head())