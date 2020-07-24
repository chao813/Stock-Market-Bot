import pymysql
import pymysql.cursors
import os

from pymysql import Error
from dotenv import load_dotenv

load_dotenv()

PATH = os.path.dirname(os.path.realpath(__file__))
STOCKS_DB_PASSWORD = os.getenv("STOCKS_DB_PASSWORD")

def create_database(conn, database):
    sql_statement = "CREATE DATABASE IF NOT EXISTS " + database  
    try:
        c = conn.cursor()
        c.execute(sql_statement)
        return conn
    except Error as e:
        print("Create database error")
        print(e)

    return conn

def create_connection(database):
    """ 
    Create a database connection to the SQLite database specified by db_file
    """
    conn = None
    try:
        conn = pymysql.connect(host="127.0.0.1",
                user="root",
                password=STOCKS_DB_PASSWORD,
                charset="utf8mb4",
                db=database,
                cursorclass=pymysql.cursors.DictCursor)
        return conn
    except Error as e:
        print("Create connection error")
        print(e)

    return conn


def create_tables(conn, sql_file_name):
    """ 
    Create a table from the create_table_sql statement
    """
    try:
        c = conn.cursor()
        execute_script_from_file(c, sql_file_name)
    except Error as e:
        print("create table error")
        print(e)


def execute_script_from_file(c, filename):
    sql_file = open(filename, "r")
    command = sql_file.read()
    sql_file.close()

    try:
        c.execute(command)
    except Error:
        print("Command skipped: {}".format(command))


def main():
    database = "stocks"
    create_stock_table_file = PATH + "/create_stock_table.sql" 
    create_stock_tracker_file = PATH + "/create_stock_tracker_table.sql" 

    conn = create_connection(database)
    if conn is None:
        print("Error! cannot create the database connection.")
    else:
        create_database(conn, database)
        create_tables(conn, create_stock_table_file)
        create_tables(conn, create_stock_tracker_file)

if __name__ == "__main__":
    main()