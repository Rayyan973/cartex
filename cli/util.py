#printing functions and stuff

import shlex
from tabulate import tabulate
from cli import db
from cli.db import log_command, log_exception

def split_args(args):
    try:
        return shlex.split(args)
    except ValueError:
        return args.split()
    
def run(command_name, sql, params=None, fetch=True):
    print(f"\n [SQL] {sql.strip()}")
    if params:
        print(f" [PARAMS] {params}")
    try:
        rows, elapsed_ms = db.execute(command_name, sql, params, fetch=fetch)
        if fetch:
            print_rows(rows)
        print(f"[OK] {len(rows) if fetch else 0} rows | {elapsed_ms:.2f}ms")
        return rows
    except Exception as exc:
        print(f"[ERROR] {str(exc)}")
        print("(error logged to logs/cartex.log)")
        return None
    
def print_rows(rows):
    if not rows:
        print("no rows")
        return
    headers = list(rows[0].keys())
    table = [[r[h] for h in headers] for r in rows ]
    print(tabulate(table, headers=headers, tablefmt="grid"))


#this is for place_order / cancel_order commands, so we can commit/rollback explicitly
def call_procedure(command_name, call_sql, params=None):
    import time
    import psycopg2.extras

    print(f"\n [SQL] {call_sql.strip()}")
    if params:
        print(f" [PARAMS] {params}")

    conn = db.get_conn()
    start = time.perf_counter()
    try:
        with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
            cur.execute(call_sql, params)
            result = cur.fetchone() if cur.description else None
        conn.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_command(command_name, call_sql, elapsed_ms, "SUCCESS")
        print(f"[OK] {elapsed_ms:.2f}ms")
        if result:
            print_rows([result])
        return result
    except Exception as exc:
        conn.rollback()
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_exception(command_name, call_sql, elapsed_ms, exc)
        print(f"[ERROR] {str(exc)}")
        print("(transaction rolled back, logged to logs/cartex.log)")
        return None
    finally:
        db.put_conn(conn)