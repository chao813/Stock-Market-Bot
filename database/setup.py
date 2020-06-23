import sqlite3 as sql
from sqlite3 import Error
import os

PATH = os.path.dirname(os.path.realpath(__file__))

def create_connection(db_file):
    """ 
    Create a database connection to the SQLite database specified by db_file
    """
    conn = None
    try:
        conn = sql.connect(db_file)
        return conn
    except Error as e:
        print("Create connection error")
        print(e)

    return conn


def create_tables(conn, create_table_sql_file):
    """ 
    reate a table from the create_table_sql statement
    """
    try:
        c = conn.cursor()
        c.executescript(create_table_sql_file)
    except Error as e:
        print("create table error")
        print(e)


def main():
    database = os.path.dirname(PATH) + "/stocks.db" 
    create_table_sql_file = open(PATH + "/create_tables.sql", "r") # dir path + "database/create_tables.sql, import config.py and pass sql variable"

    conn = create_connection(database)

    if conn is None:
        print("Error! cannot create the database connection.")

    create_tables(conn, create_table_sql_file.read())


if __name__ == "__main__":
    main()