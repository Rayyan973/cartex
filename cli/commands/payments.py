#payments view/update

from cli.util import run, split_args

def view_payment(args):
    if len(args) != 1:
        print("usage: payments view <order_id>")
        return
    sql = "SELECT payment_id, order_id, amount, status, paid_at FROM payments WHERE order_id = %s;"
    run("payments view", sql, (args[0],))


def update_payment(args):
    if len(args) != 2:
        print("usage: payments update <order_id> <status>")
        return
    order_id, status = args
    # updates payment status and sets paid_at to current time if and only if status=paid
    sql = "UPDATE payments SET status=%s, paid_at= CASE WHEN %s='paid' \
        THEN now() ELSE paid_at END WHERE order_id=%s RETURNING payment_id, order_id, amount, status, paid_at;"
    run("payments update", sql, (status, status, order_id))


def dispatch(arg):
    parts = split_args(arg)
    if not parts:
        print("Usage: payments <view|update> [...]")
        return
    sub, rest = parts[0], parts[1:]
    if sub == "view":
        view_payment(rest)
    elif sub == "update":
        update_payment(rest)
    else:
        print(f"unknown payments subcommand: {sub}")