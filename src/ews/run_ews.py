from rule_engine import run_all_borrowers
from zone_classifier import run_classification
from alert_notifier import run_alerts


def main():
    print("=" * 60)
    print("EWS PIPELINE START")
    print("=" * 60)

    print("\n[1/3] Running rule engine...")
    signals = run_all_borrowers()
    print(f"      → {len(signals)} signals detected")

    print("\n[2/3] Classifying borrower zones...")
    zones = run_classification()
    print(f"      → {zones.groupby('zone').size().to_dict()}")

    print("\n[3/3] Sending alerts...")
    run_alerts()

    print("\n" + "=" * 60)
    print("EWS PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()