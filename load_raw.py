import csv
import os
from pathlib import Path
import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DB = dict(host="localhost", port=3306, user= os.environ["MYSQL_USER"],
          password= os.environ["MYSQL_PASSWORD"], charset="utf8mb4")

CLEAN = Path("data/clean")
FILES = {
    "modules": "modules.csv",
    "events": "events.csv",
    "event_resources": "event_resources.csv",
}

def load(cur, table, csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        # empty CSV cells become real NULLs in MySQL
        rows = [tuple(r[c] if r[c] != "" else None for c in cols) for r in reader]
    col_sql = ", ".join(f"`{c}`" for c in cols)
    placeholders = ", ".join(["%s"] * len(cols))
    cur.execute(f"TRUNCATE TABLE tt_raw.{table}")
    cur.executemany(
        f"INSERT INTO tt_raw.{table} ({col_sql}) VALUES ({placeholders})", rows
    )
    return len(rows)

conn = pymysql.connect(**DB)
try:
    with conn.cursor() as cur:
        for table, fname in FILES.items():
            n = load(cur, table, CLEAN / fname)
            print(f"tt_raw.{table}: {n} rows loaded")
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("SELECT source_code, faculty, `period` FROM tt_raw.modules LIMIT 3")
        print(cur.fetchall())
        cur.execute("SELECT event_id, day_index, start_time, raw_weeks FROM tt_raw.events LIMIT 3")
        print(cur.fetchall())
finally:
    conn.close()