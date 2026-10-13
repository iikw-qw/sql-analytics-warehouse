from pathlib import Path

import pandas as pd

QUERY_DIR = Path(__file__).resolve().parent.parent / "queries"


def list_queries():
    return sorted(p.stem for p in QUERY_DIR.glob("*.sql"))


def run_query(conn, name, params=None):
    sql = (QUERY_DIR / f"{name}.sql").read_text(encoding="utf-8")
    return pd.read_sql_query(sql, conn, params=params or {})
