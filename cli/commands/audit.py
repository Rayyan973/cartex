from cli.util import run, split_args

def show_log():
    sql = (
        "SELECT log_id, table_name, record_id, action, old_value, new_value, changed_at "
        "FROM audit_log ORDER BY changed_at DESC LIMIT 20;"
    )
    run("audit log", sql)

def dispatch(arg):
    parts = split_args(arg)
    if not parts or parts[0] != "log":
        print("usage: audit log")
        return
    show_log(parts[1:])