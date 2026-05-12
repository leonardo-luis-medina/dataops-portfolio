import csv
import sqlite3
import os
from datetime import datetime

DB_PATH = "data/sales.db"
CSV_PATH = "data/sales.csv"

def run_etl():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"No data file at {CSV_PATH} — run generate_data.py first")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            order_id TEXT PRIMARY KEY,
            product TEXT,
            region TEXT,
            quantity INTEGER,
            price REAL,
            timestamp TEXT,
            total REAL,
            loaded_at TEXT
        )
    """)

    inserted = 0
    skipped = 0

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total = round(float(row["quantity"]) * float(row["price"]), 2)
            try:
                cur.execute("""
                    INSERT INTO sales VALUES (?,?,?,?,?,?,?,?)
                """, (
                    row["order_id"],
                    row["product"],
                    row["region"],
                    int(row["quantity"]),
                    float(row["price"]),
                    row["timestamp"],
                    total,
                    datetime.now().isoformat()
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM sales")
    total_rows = cur.fetchone()[0]

    cur.execute("SELECT SUM(total) FROM sales")
    total_revenue = round(cur.fetchone()[0] or 0, 2)

    conn.close()

    print(f"✅ ETL complete — inserted: {inserted}, skipped: {skipped}")
    print(f"📊 Total rows in DB: {total_rows}")
    print(f"💰 Total revenue: ₱{total_revenue:,.2f}")

    return inserted, total_rows, total_revenue

if __name__ == "__main__":
    run_etl()