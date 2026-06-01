import hashlib
import json
import sqlite3
from pathlib import Path


def _row_hash(row: dict) -> str:
    stable = json.dumps(row, sort_keys=True, default=str)
    return hashlib.sha256(stable.encode()).hexdigest()


def _ensure_table(conn: sqlite3.Connection, table: str, columns: list[dict]) -> None:
    col_defs = []
    for col in columns:
        if col.get("type") == "numeric":
            col_defs.append(f'"{col["name"]}" REAL')
        else:
            col_defs.append(f'"{col["name"]}" TEXT')
    col_defs_sql = ", ".join(col_defs)
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS "{table}" (
            _row_hash TEXT PRIMARY KEY,
            {col_defs_sql}
        )
        """
    )
    conn.commit()


def load_rows(
    rows: list[dict],
    schema: list[dict],
    db_path: str,
    table_name: str,
) -> int:
    if not rows:
        return 0

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    _ensure_table(conn, table_name, schema)

    col_names = [col["name"] for col in schema]
    placeholders = ", ".join(["?"] * (len(col_names) + 1))
    col_list = ", ".join(['"_row_hash"'] + [f'"{c}"' for c in col_names])
    sql = (
        f'INSERT OR IGNORE INTO "{table_name}" ({col_list}) VALUES ({placeholders})'
    )

    inserted = 0
    for row in rows:
        h = _row_hash({k: row.get(k) for k in col_names})
        values = [h] + [row.get(c) for c in col_names]
        cursor = conn.execute(sql, values)
        if cursor.rowcount:
            inserted += 1

    conn.commit()
    conn.close()
    return inserted
