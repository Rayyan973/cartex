#!usr/bin/env python3

#to load cartex schema and seed data (if flag is set)

import os
import sys
import glob
import psycopg2

SCHEMA_FILES = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "schema", "*.sql")))
SEED_FILE = os.path.join(os.path.dirname(__file__), "seed", "seed_data.sql")

def get_conn():
    return psycopg2.connect(
        host = "localhost",
        port = 5432,
        dbname = "cartex",
        user = "postgres",
        password = "postgres"
    )

def run_file(cur, path):
    print(f"Applying {os.path.relpath(path)}...")
    with open(path, "r") as f:
        cur.execute(f.read())

def main():
    seed = "--seed" in sys.argv

    conn = get_conn()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            for path in SCHEMA_FILES:
                run_file(cur, path)
            if seed:
                run_file(cur, SEED_FILE)
        conn.commit()
        print("Schema applied successfully." + (" Seed data also applied." if seed else ""))
    except Exception as e:
        conn.rollback()
        print(f"Error applying schema: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()