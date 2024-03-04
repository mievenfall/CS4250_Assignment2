#-------------------------------------------------------------------------
# AUTHOR: Evelyn Vu
# FILENAME: db_create_tables.py
# SPECIFICATION: Create tables Categories, Documents, Terms, Index in database corpus using PostgreSQL
# FOR: CS 4250- Assignment #2
# TIME SPENT: 7
#-----------------------------------------------------------*/


from psycopg2 import *


def createTables():
    DB_NAME = "corpus"
    DB_USER = "postgres"
    DB_PASS = "YOUR_PASSWORD"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = connect(
            database=DB_NAME,
            user=DB_USER,
            password = DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )

        curr = conn.cursor()
        create_categories_table = "CREATE TABLE IF NOT EXISTS Categories (id_cat INTEGER NOT NULL, name VARCHAR(100) NOT NULL, PRIMARY KEY (id_cat));"
        create_documents_table = "CREATE TABLE IF NOT EXISTS Documents (doc INTEGER NOT NULL, text VARCHAR(100) NOT NULL, title VARCHAR(100) NOT NULL, num_chars INTEGER NOT NULL, date DATE NOT NULL, id_cat INTEGER NOT NULL, PRIMARY KEY (doc), FOREIGN KEY (id_cat) REFERENCES Categories(id_cat));"
        create_terms_table = "CREATE TABLE IF NOT EXISTS Terms (term VARCHAR(100) NOT NULL, num_chars INTEGER NOT NULL, PRIMARY KEY (term));"
        create_index_table = "CREATE TABLE IF NOT EXISTS Index (term VARCHAR(100) NOT NULL, doc INTEGER NOT NULL, term_count INTEGER NOT NULL, PRIMARY KEY(term, doc), FOREIGN KEY (term) REFERENCES Terms(term), FOREIGN KEY (doc) REFERENCES Documents(doc));"
        curr.execute(create_categories_table + create_documents_table + create_terms_table + create_index_table)
        conn.commit()

    except Exception as e:
        print("Create table error: " + str(e))


if __name__ == "__main__":
    createTables()