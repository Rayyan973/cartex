#code for 'users list/add/delete'

from cli.util import run, split_args

def list_users():
    sql = "SELECT user_id, name, email, created_at FROM users ORDER BY user_id;"
    run("users list", sql)

def add_user(args):
    if len(args) < 2:
        print("usage: users add <name> <email>")
        return
    name = " ".join(args[:-1]) #gotta do it like this because name can have spaces
    email = args[-1]
    sql = "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING user_id, name, email, created_at;"
    run("users add", sql, params=(name, email))

def delete_user(args):
    if len(args) != 1:
        print("usage: users delete <user_id>")
        return
    user_id = args[0]
    sql = "DELETE FROM users WHERE user_id = %s RETURNING user_id, name, email, created_at;"
    run("users delete", sql, params=(user_id,)) #comma is to make it a tuple

def dispatch(arg):
    parts = split_args(arg)
    if not parts:
        print("usage: users <list|add|delete> [...]")
        return
    sub, rest = parts[0], parts[1:]

    if sub == "list":
        list_users()
    elif sub == "add":
        add_user(rest)
    elif sub == "delete":
        delete_user(rest)
    else:
        print(f"unknown cmd {sub}, usage: users <list|add|delete> [...]")