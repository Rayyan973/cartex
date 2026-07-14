#!/usr/bin/env python3

import os
import sys
import cmd

#hack to make sure import cmds work even tho main.py is in another directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.commands import users, products, cart, orders, payments, analytics, audit, rawsql
from cli.db import db, logger

#ai-generated banner art :))
BANNER = r"""
   ______           __
  / ____/___ ______/ /____  _  __
 / /   / __ `/ ___/ __/ _ \| |/_/
/ /___/ /_/ / /  / /_/  __/>  <
\____/\__,_/_/   \__/\___/_/|_|

Cartex - Postgres e-commerce engine. Type `help` for commands.
"""

class CartexShell(cmd.Cmd):
    intro = BANNER
    prompt = 'cartex> '

    #here we're defining all the cmds that you can use in the shell, each file has a dispatch function
    def do_users(self, arg):
        """users list | users add <name> <email> | users delete <id>"""
        users.dispatch(arg)

    def do_products(self, arg):
        """products list | products search <keyword> | products add <name> <price> <stock> [category_id] [description] | products update <id> <price> | products delete <id>"""
        products.dispatch(arg)

    def do_cart(self, arg):
        """cart add <user_id> <product_id> <qty> | cart view <user_id> | cart clear <user_id>"""
        cart.dispatch(arg)

    def do_orders(self, arg):
        """orders place <user_id> <shipping_address> | orders view <user_id> | orders cancel <order_id> | orders status <order_id>"""
        orders.dispatch(arg)
    
    def do_payments(self, arg):
        """payments view <order_id> | payments update <order_id> <status>"""
        payments.dispatch(arg)
    
    def do_analytics(self, arg):
        """analytics revenue | analytics top_products | analytics clv | analytics low_stock"""
        analytics.dispatch(arg)

    def do_audit(self, arg):
        """audit log - prints the last 20 rows of audit_log"""
        audit.dispatch(arg)

    def do_sql(self, arg):
        """sql <raw query> - execute any raw SQL and print results as a table"""
        rawsql.dispatch(arg)

    def do_exit(self, arg):
        """exit - quit cartex"""
        print("seeya later alligator")
        db.close_all()
        return True

    def do_quit(self, arg):
        """quit - duh, same as exit"""
        return self.do_exit(arg)
    
    def emptyline(self):
        #the commands default is to repeat the last command, setting it to pass removes that
        pass

    def default(self, line):
        print(f"Unknown cmd: {line}. get help man (type 'help')")


def main():
    try:
        #this is a type of arduino void loop
        CartexShell().cmdloop()
    except KeyboardInterrupt:
        print("\nbye byeeeeee..")
        db.close_all()

if __name__ == '__main__':
    main()