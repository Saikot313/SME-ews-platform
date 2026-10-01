
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "../../data/sme_ews.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def build_alert_message(borrower_id, zone, previous_zone, score, n_signals):
    if previous_zone and previous_zone != zone:
        return (f"BORROWER ZONE CHANGE: {borrower_id} moved from "
                f"{previous_zone} → {zone}. Score={score}, "
                f"Active signals={n_signals}.")
    return (f"RED ZONE ALERT: {borrower_id} is in {zone}. "
            f"Score={score}, Active signals={n_signals}.")


def get_rm_email(borrower_id):
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT relationship_manager FROM borrowers WHERE borrower_id = ?",
            conn, params=(borrower_id,)
        )
    if df.empty:
        return "rm@idlc.com"
    rm = df["relationship_manager"].iloc[0]
    return rm.lower().replace(" ", ".") + "@idlc.com"


def send_alert(alert):
   
    print(f"[ALERT] → {alert['notified_to']}: {alert['alert_message']}")
    return "Sent"


def run_alerts():
    with get_conn() as conn:
        zones = pd.read_sql(
            "SELECT * FROM borrower_zones "
            "WHERE as_of_date = (SELECT MAX(as_of_date) FROM borrower_zones)",
            conn
        )

    alerts = []
    for _, z in zones.iterrows():
       
        zone_changed = (
            z["previous_zone"] is not None and
            z["previous_zone"] != z["zone"]
        )
        is_red = z["zone"] == "Red"

        if not (zone_changed or is_red):
            continue

        message = build_alert_message(
            z["borrower_id"], z["zone"], z["previous_zone"],
            z["total_score"], z["active_signals"]
        )
        alert = {
            "borrower_id": z["borrower_id"],
            "alert_date": datetime.now(),
            "alert_type": "ZoneChange" if zone_changed else "RedZone",
            "alert_message": message,
            "severity": "High" if z["zone"] == "Red" else "Medium",
            "notified_to": get_rm_email(z["borrower_id"]),
            "notification_status": "Pending",
            "acknowledged": False,
        }
        alert["notification_status"] = send_alert(alert)
        alerts.append(alert)

    if alerts:
        df = pd.DataFrame(alerts)
        with get_conn() as conn:
            df.to_sql("alerts", conn, if_exists="append", index=False)
        print(f"\nSent {len(alerts)} alerts")
    else:
        print("No alerts to send.")


if __name__ == "__main__":
    run_alerts()