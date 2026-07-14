#orders <place/view/cancel/status>

import time
import psycopg2.extras

from cli.db import db, log_command, log_exception
from cli.util import run, print_rows, split_args


def place_order(args):
    if len(args) < 2:
        print("usage: orders place <user_id> <shipping_address...> ")
        return
    user_id = args[0]
    shipping_address = " ".join(args[1:])

    #first read the cart (just a lookup)
    cart_sql = "SELECT product_id, quantity FROM cart_items WHERE user_id = %s ORDER BY cart_item_id;"
    print(f"\n[SQL] {cart_sql}")
    print(f" [PARAMS] {(user_id,)}")

    try:
        cart_rows, elapsed_ms = db.execute("orders place (read cart)", cart_sql, (user_id,))
    except Exception as e:
        log_exception("orders place (read cart) error: ", e)
        print(f"[ERROR] reading cart for user {user_id}: {e}")
        return

    if not cart_rows:
        print(f"[ERROR] nothing in cart, no order for you today man.")
        return
    
    product_ids = [row['product_id'] for row in cart_rows]
    quantities = [row['quantity'] for row in cart_rows]

    #now place the order
    call_sql = "CALL place_order(%s, %s, %s, %s, NULL);"
    params = (user_id, product_ids, quantities, shipping_address)
    print(f"\n[SQL] {call_sql}")
    print(f" [PARAMS] {params}")

    conn = db.get_conn()
    start = time.perf_counter()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(call_sql, params)
            result = cur.fetchone()
            conn.commit()
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_command("orders place", call_sql, elapsed_ms, "SUCCESS")
            print(f"[OK] order placed successfully | {elapsed_ms:.2f} ms")
            
            if result:
                print_rows([result])
    except Exception as e:
        conn.rollback()
        log_exception("orders place", call_sql, elapsed_ms, e)
        print(f"[ERROR] {e}")
        print("txn was rolled back, no order placed")
    finally:
        db.put_conn(conn)


def view_orders(args):
    # calls the get_order_history stored procedure, which opens a refcursor that we FETCH from inside the same txn
    if len(args) != 1:
        print("usage: orders view <user_id>")
        return
    user_id = args[0]

    call_sql = "CALL get_order_history(%s, 'order_history_cursor');"
    fetch_sql = "FETCH ALL FROM order_history_cursor;"
    print(f"\n[SQL] {call_sql}")
    print(f"\n[SQL] {fetch_sql}")
    print(f" [PARAMS] {(user_id,)}")

    conn = db.get_conn()
    start = time.perf_counter()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(call_sql, (user_id,))
            cur.execute(fetch_sql)
            rows = cur.fetchall()
        conn.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_command("orders view", call_sql+" "+fetch_sql, elapsed_ms, "SUCCESS")
        print_rows(rows)
        print(f"[OK] {len(rows)} rows | {elapsed_ms:.2f} ms")
    except Exception as e:
        conn.rollback()
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_exception("orders view", call_sql, elapsed_ms, e)
        print(f"[ERROR] {e}")
    finally:
        db.put_conn(conn)


def cancel_order(args):
    if len(args) != 1:
        print("Usage: orders cancel <order_id>")
        return
    order_id = args[0]
    call_sql = "CALL cancel_order(%s);"

    print(f"\n[SQL] {call_sql}")
    print(f"[PARAMS] {(order_id,)}")

    conn = db.get_conn()
    start = time.perf_counter()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(call_sql, (order_id,))
        conn.commit()
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_command("orders cancel", call_sql, elapsed_ms, "SUCCESS")
        print(f"[OK] Order {order_id} cancelled, stock restored | {elapsed_ms:.2f} ms")
    except Exception as exc:
        conn.rollback()
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_exception("orders cancel", call_sql, elapsed_ms, exc)
        print(f"[ERROR] {exc}")
    finally:
        db.put_conn(conn)

def order_status(args):
    if len(args) != 1:
        print("Usage: orders status <order_id>")
        return
    sql = "SELECT order_id, status, total_amount, updated_at FROM orders WHERE order_id = %s;"
    run("orders status", sql, (args[0],))


def dispatch(arg):
    parts = split_args(arg)
    if not parts:
        print("Usage: orders <place|view|cancel|status> [...]")
        return
    sub, rest = parts[0], parts[1:]
    if sub == "place":
        place_order(rest)
    elif sub == "view":
        view_orders(rest)
    elif sub == "cancel":
        cancel_order(rest)
    elif sub == "status":
        order_status(rest)
    else:
        print(f"Unknown orders subcommand: {sub}")