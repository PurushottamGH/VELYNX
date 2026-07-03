import sqlite3
import glob

print("Scanning for 'Avatar' in all .db files...")

for db_path in glob.glob("**/*.db", recursive=True):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # First, check if the table even exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relationships'")
        if cursor.fetchone():
            # Now search for Avatar
            cursor.execute("SELECT * FROM relationships WHERE subject LIKE '%avatar%' OR object LIKE '%avatar%'")
            results = cursor.fetchall()
            if results:
                print(f"[!] FOUND GHOST AVATAR IN: {db_path}")
                for row in results:
                    print(f"    {row}")
        conn.close()
    except Exception as e:
        continue

print("Scan complete.")
