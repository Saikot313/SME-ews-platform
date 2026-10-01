
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# Paths
DB_PATH = os.getenv("DB_PATH", str(ROOT_DIR / "data" / "sme_ews.db"))
VAULT_DIR = os.getenv("VAULT_DIR", str(ROOT_DIR / "data" / "portal_uploads"))
DATA_DIR = ROOT_DIR / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_PDF_DIR = DATA_DIR / "raw" / "pdf_statements"

for p in [DATA_DIR, SYNTHETIC_DIR, PROCESSED_DIR, RAW_PDF_DIR,
          Path(VAULT_DIR)]:
    p.mkdir(parents=True, exist_ok=True)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Portal
PORTAL_PORT = int(os.getenv("PORTAL_PORT", 4040))

# Alerts (production)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
ALERT_FROM_EMAIL = os.getenv("ALERT_FROM_EMAIL", "alerts@idlc.com")