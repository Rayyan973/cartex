#products list/search/add/update/delete

from cli.util import run, split_args

def list_products():
    sql = "SELECT product_id, name, price, stock, category_id FROM products ORDER BY product_id LIMIT 50;"
    run("products list", sql)

def search_products(args):
    if not args:
        print("usage: products search <whatever you wanna search for>")
        return
    term = " ".join(args)
    #using full text search to find keyword in name or description
    sql = "SELECT product_id, name, price, stock, category_id FROM products \
        WHERE to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')) \
            @@ plainto_tsquery('english', %s) \
        ORDER BY product_id LIMIT 50;"
    run("products search", sql, (term,))

def add_product(args):
    if len(args) < 3:
        print("usage: products add <name> <price> <stock> [category_id] [description]")
        return
    name, price, stock = args[0], args[1], args[2]
    category_id = args[3] if len(args) > 3 else None
    description = " ".join(args[4:]) if len(args) > 4 else None

    sql = "INSERT INTO products(name, description, price, stock, category_id) \
        VALUES (%s, %s, %s, %s, %s) RETURNING product_id, name, price, stock, category_id;"
    run("products add", sql, (name, description, price, stock, category_id))


def update_product(args):
    if len(args) != 2:
        print("usage: products update <id> <price>")
        return
    product_id, price = args
    sql = "UPDATE products SET price=%s WHERE product_id=%s RETURNING product_id, name, price;"
    run("products update", sql, (price, product_id))

def delete_product(args):
    if len(args) != 1:
        print("usage: products delete <id>")
        return
    product_id = args[0]
    sql = "DELETE FROM products WHERE product_id=%s RETURNING product_id;"
    run("products delete", sql, (product_id,))

def dispatch(arg):
    parts = split_args(arg)
    if not parts:
        print("usage: products <list|search|add|update|delete> [...]")
        return
    sub, rest = parts[0], parts[1:]

    if sub == "list":
        list_products()
    elif sub == "search":
        search_products(rest)
    elif sub == "add":
        add_product(rest)
    elif sub == "update":
        update_product(rest)
    elif sub == "delete":
        delete_product(rest)
    else:
        print(f"unknown cmd, usage: products <list/search/add/update/delete> [...]")