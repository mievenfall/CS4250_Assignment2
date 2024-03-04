#-------------------------------------------------------------------------
# AUTHOR: Evelyn Vu
# FILENAME: db_create_database.py
# SPECIFICATION: Create database corpus using PostgreSQL
# FOR: CS 4250- Assignment #2
# TIME SPENT: 7
#-----------------------------------------------------------*/

from psycopg2 import *


def createDatabase():
    DB_NAME = "corpus"
    DB_USER = "postgres"
    DB_PASS = "YOUR_PASSWORD"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = connect(
            user=DB_USER,
            password = DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        curr = conn.cursor()
        create_database = "CREATE DATABASE {} TEMPLATE template0 ENCODING 'UTF8';".format(DB_NAME)
        curr.execute(create_database)
        conn.commit()

    except Exception as e:
        print("Create database error: " + str(e))

if __name__ == "__main__":
    createDatabase()