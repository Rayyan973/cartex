#cart <add/view/clear>

from cli.util import run, split_args

def add_to_cart(args):
    if len(args) != 3:
        print("usage: cart add <user_id> <product_id> <qty>")
        return
    user_id, product_id, qty = args
    sql = "INSERT INTO cart_items(user_id, product_id, quantity) \
        VALUES (%s, %s, %s);\
        ON CONFLICT (user_id, product_id) DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity;\
        RETURNING cart_item_id, user_id, product_id, quantity;"
    run("cart add", sql, (user_id, product_id, qty))

def view_cart(args):
    if len(args) != 1:
        print("usage: cart view <user_id>")
        return
    user_id = args[0]
    sql = "SELECT ci.cart_item_id, p.product_id, p.name, p.price, ci.quantity, (p.price*ci.quantity) AS line_total\
        FROM cart_items ci\
        JOIN products p ON p.product_id=ci.product_id\
        WHERE ci.user_id = %s \
        ORDER BY ci.cart_item_id;"
    run("cart view", sql, (user_id,)) #comma is to make it a tuple

def clear_cart(args):
    if len(args) != 1:
        print("usage: cart clear <user_id>")
        return
    user_id = args[0]
    sql = "DELETE FROM cart_items WHERE user_id = %s RETURNING cart_item_id;"
    run("cart clear", sql, (user_id,))

def dispatch(arg):
    parts = split_args(arg)
    if not parts:
        print("usage: cart <add/view/clear> [...]")
        return
    sub, rest = parts[0], parts[1:]

    if sub == "add":
        add_to_cart(rest)
    elif sub == "view":
        view_cart(rest)
    elif sub == "clear":
        clear_cart(rest)
    else:
        print(f"unknown cmd, usage: cart <add/view/clear> [...]")