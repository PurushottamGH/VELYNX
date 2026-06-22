import sqlite3

# Change this if Step 1 gave you a different name!
db_path = "velynx_state.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
SELECT name, sql
FROM sqlite_master
WHERE type='table'
ORDER BY name;
""")

for table_name, create_sql in cursor.fetchall():
    print("\n" + "=" * 80)
    print(table_name)
    print("=" * 80)
    if create_sql:
        print(create_sql)
    else:
        print("(No schema available / Internal table)")

conn.close()