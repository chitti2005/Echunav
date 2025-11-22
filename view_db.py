import sqlite3

DB_PATH = 'database.db'   # change path if your DB is elsewhere

def view_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        data = cur.execute(f"SELECT * FROM {table_name}").fetchall()
        if not data:
            print(f"⚠️ Table '{table_name}' is empty.\n")
            return
        print(f"\n📊 Contents of table: {table_name}")
        print("-" * 60)
        # print headers
        print(" | ".join(data[0].keys()))
        print("-" * 60)
        # print rows
        for row in data:
            print(" | ".join(str(v) for v in row))
        print("\n")
    except sqlite3.OperationalError as e:
        print(f"❌ Error reading table '{table_name}': {e}")
    conn.close()

if __name__ == "__main__":
    tables = ["voters", "candidates", "logs", "otp_log", "admin"]
    for t in tables:
        view_table(t)
