import pymysql
import pymysql.cursors
import os

from dotenv import load_dotenv

load_dotenv()

STOCKS_DB_PASSWORD = os.getenv("STOCKS_DB_PASSWORD")

class Database:
    def __init__(self, name):
        self._con = pymysql.connect(host="127.0.0.1",
                user="root",
                password=STOCKS_DB_PASSWORD,
                charset="utf8mb4",
                db=name,
                cursorclass=pymysql.cursors.DictCursor)
        self._cursor = self._con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._con

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()