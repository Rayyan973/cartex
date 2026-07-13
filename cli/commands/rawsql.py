#usage: 'sql <raw query>'

from cli.util import run

def dispatch(arg):
    query = arg.strip()
    if not query:
        print("usage: sql <raw query>")
        return
    fetch = query.lower().lstrip().startswith(("select", "with", "show"))
    run("sql", query, fetch=fetch)