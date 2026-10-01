"""
SQLite/SQLAlchemy DB helper.
Provides engine + session + quick query functions.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from .config import DB_PATH
from .logger import get_logger

log = get_logger(__name__)


@contextmanager
def get_conn():
    """Context manager for SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        log.error(f"DB error: {e}")
        raise
    finally:
        conn.close()


def query(sql: str, params: tuple = None) -> pd.DataFrame:
    """Run a SELECT and return DataFrame."""
    with get_conn() as conn:
        return pd.read_sql(sql, conn, params=params)


def execute(sql: str, params: tuple = None) -> None:
    """Run INSERT/UPDATE/DELETE."""
    with get_conn() as conn:
        conn.execute(sql, params or ())


def insert_df(df: pd.DataFrame, table: str, if_exists: str = "append"):
    """Insert a DataFrame into a table."""
    with get_conn() as conn:
        df.to_sql(table, conn, if_exists=if_exists, index=False)
    log.info(f"Inserted {len(df)} rows into {table}")