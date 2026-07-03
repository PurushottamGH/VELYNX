import sqlite3
from pathlib import Path

def inspect():
    # Search for all graph.db files in your project
    root = Path(r"C:\Users\Purushottam\Documents\VELYNX")
    db_files = list(root.glob("**/graph.db"))
    
    print(f"Found {len(db_files)} database files:\n")
    
    for db in db_files:
        print(f"Checking: {db}")
        try:
            conn = sqlite3.connect(db)
            count = conn.execute("SELECT count(*) FROM triples").fetchone()[0]
            print(f" -> Row count: {count}")
            if count > 0:
                print(" -> DATA FOUND HERE!")
            conn.close()
        except Exception as e:
            print(f" -> Could not read: {e}")
        print("-" * 40)

if __name__ == "__main__":
    inspect()
