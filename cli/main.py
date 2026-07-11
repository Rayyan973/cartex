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
        users.dispatch(arg)

    def do_products(self, arg):
        products.dispatch(arg)

    def do_cart(self, arg):
        cart.dispatch(arg)

    def do_orders(self, arg):
        orders.dispatch(arg)
    
    def do_payments(self, arg):
        payments.dispatch(arg)
    
    def do_analytics(self, arg):
        analytics.dispatch(arg)

    def do_audit(self, arg):
        audit.dispatch(arg)

    def do_sql(self, arg):
        rawsql.dispatch(arg)

    def do_exit(self, arg):
        print("seeya later alligator")
        db.close_all()
        return True

    def do_quit(self, arg):
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        print()
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