from cli.util import run, split_args

def revenue():
    run("analytics revenue", "SELECT * FROM revenue_by_category;")

def top_products():
    run("analytics top_products", "SELECT * FROM top_products_sold LIMIT 20;")

def clv():
    run("analytics clv", "SELECT * FROM customer_lifetime_value LIMIT 20;")

def low_stock():
    run("analytics low_stock", "SELECT * FROM low_stock_alerts;")


def dispatch(arg):
    parts = split_args(arg)
    if not parts:
        print("usage: analytics <revenue|top_products|clv|low_stock> {clv -> customer lifetime value}")
        return
    sub = parts[0]
    if sub == "revenue":
        revenue()
    elif sub == "top_products":         
        top_products()
    elif sub == "clv":
        clv()
    elif sub == "low_stock":
        low_stock()
    else:
        print(f"unknown cmd {sub}, usage: analytics <revenue|top_products|clv|low_stock>")