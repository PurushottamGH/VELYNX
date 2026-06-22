import sqlite3
import glob

TARGET = "avatar"

for db in glob.glob("**/*.db", recursive=True) + glob.glob("**/*.sqlite3", recursive=True):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        for (table,) in tables:
            cols = cur.execute(f"PRAGMA table_info({table})").fetchall()
            text_cols = [c[1] for c in cols]  # Optional filter logic
            try:
                rows = cur.execute(f"SELECT * FROM {table}").fetchall()
                for row in rows:
                    if TARGET in str(row).lower():
                        print(f"\n[!] GHOST FOUND: {db}")
                        print(f"TABLE: {table} | ROW: {row}")
            except Exception:
                pass
        conn.close()
    except Exception:
        pass
