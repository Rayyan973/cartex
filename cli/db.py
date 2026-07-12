#query executor and logging logic is done in this file

import os
import time
import logging
import traceback
import psycopg2
import psycopg2.pool
import psycopg2.extras

#same thing as main.py
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'cartex.log')

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

class CartexLoggingFormatter(logging.Formatter):
    #formats log lines as "[TIMESTAMP] [LEVEL] COMMAND | SQL | TIME | STATUS"

    def format(self, record):
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        command = getattr(record, "command", "-")
        sql = getattr(record, "sql", "-")
        time_ms = getattr(record, "time_ms", "-")
        status = getattr(record, "status", "-")
        base = f"[{timestamp}] [{record.levelname}] {command} | {sql} | {time_ms}ms | {status}"

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        elif record.getMessage():
            base += f"\n{record.getMessage()}"

        return base
    


def setup_logger():
    _ensure_log_dir()
    logger = logging.getLogger("cartex")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(CartexLoggingFormatter())
        logger.addHandler(handler)
    return logger
    
    
logger = setup_logger()


def log_command(command, sql, time_ms, status, level=logging.INFO, extra_message=""):

    logger.log(
        level,
        extra_message,
        extra={
            "command": command,
            "sql": (str(sql) or "-").replace("\n", " ").strip(),
            "time_ms": f"{float(time_ms):.2f}ms",
            "status": status
        },
    )


def log_exception(command, sql, time_ms, exc):
    logger.error(
        traceback.format_exc(),
        extra={
            "command": command,
            "sql": (str(sql) or "-").replace("\n", " ").strip(),
            "time_ms": f"{float(time_ms):.2f}ms",
            "status": "FAILURE",
            "error": str(exc),
        },
    )



#connection stuff
class Database:
    def __init__(self):
        self.dsn = dict(
            host = "localhost",
            port = 5432,
            dbname = "cartex",
            user = "postgres",
            password = "postgres",
        )
        self.pool = psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=10, **self.dsn)

    def get_conn(self):
        conn = self.pool.getconn()
        conn.autocommit = False
        return conn
    
    def put_conn(self, conn):
        self.pool.putconn(conn)

    def close_all(self):
        self.pool.closeall()

    
    #execution logic
    def execute(self, command, sql, params=None, fetch=True):
        conn = self.get_conn()
        start = time.perf_counter()
        try:
            with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() if fetch and cur.description else []
            conn.commit()
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_command(command, sql, elapsed_ms, "SUCCESS")
            return rows, elapsed_ms
        except Exception as exc:
            conn.rollback()
            elapsed_ms = (time.perf_counter() - start) * 1000
            log_exception(command, sql, elapsed_ms, exc)
            raise
        finally:
            self.put_conn(conn)


db = Database()