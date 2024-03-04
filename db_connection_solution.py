#-------------------------------------------------------------------------
# AUTHOR: Evelyn Vu
# FILENAME: db_connection_solution.py
# SPECIFICATION: Manage inverted index of tables in database corpus using PostgreSQL
# FOR: CS 4250- Assignment #2
# TIME SPENT: 7
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
# --> add your Python code here
from psycopg2 import *


def connectDataBase():

    # Create a database connection object using psycopg2
    # --> add your Python code here
    DB_NAME = "corpus"
    DB_USER = "postgres"
    DB_PASSWORD = "Xxqfjc$7"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = connect(
            database=DB_NAME,
            user=DB_USER,
            password = DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    
    except Exception as e:
        print("Connect database error: " + str(e))


def createCategory(cur, catId, catName):

    # Insert a category in the database
    # --> add your Python code here
    query = "INSERT INTO Categories (id_cat, name) VALUES (%(id_cat)s, %(name)s);"
    param = {'id_cat': catId, 'name': catName}

    try:
        cur.execute(query, param)
    except Exception as e:
        print("Create category error: " + str(e))


def createDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Get the category id based on the informed category name
    # --> add your Python code here
    get_cat_id_query = "SELECT Categories.id_cat FROM Categories WHERE Categories.name = %(docCat)s;"
    get_cat_id_param = {'docCat': docCat}
    
    cur.execute(get_cat_id_query, get_cat_id_param)

    cat_result = cur.fetchall()

    # If the sql results nothing -> invalid category name
    if len(cat_result) == 0:
        print("Invalid category name")
        return
    
    cat_id = cat_result[0]

    # 2 Insert the document in the database. For num_chars, discard the spaces and punctuation marks.
    # --> add your Python code here
    try:
        insert_doc_query = "INSERT INTO Documents (doc, text, title, num_chars, date, id_cat) VALUES (%(doc)s, %(text)s, %(title)s, %(num_chars)s, %(date)s, %(id_cat)s);"
        insert_doc_param = {'doc': docId, 'text': docText, 'title':docTitle, 'num_chars': str(len(docText)), 'date': docDate, 'id_cat':cat_id}

        cur.execute(insert_doc_query, insert_doc_param)

    # 3 Update the potential new terms.
    # 3.1 Find all terms that belong to the document. Use space " " as the delimiter character for terms and Remember to lowercase terms and remove punctuation marks.
    # 3.2 For each term identified, check if the term already exists in the database
    # 3.3 In case the term does not exist, insert it into the database
    # --> add your Python code here
        
        # Strip all punctuation from docText
        docText_no_punct = ''.join(char for char in docText if char.isalnum() or char == ' ')

        # Split words in docText into list
        terms = docText_no_punct.lower().split(" ")

        for term in terms:
            get_term_query = "SELECT * FROM Terms WHERE Terms.term = %(term)s;"
            get_term_param = {'term': term}

            cur.execute(get_term_query, get_term_param)

            term_result = cur.fetchall()

            # If the sql results nothing -> term does not exist -> add term into the table
            if len(term_result) == 0:
                insert_term_query = "INSERT INTO Terms (term, num_chars) VALUES (%(term)s, %(num_chars)s);"
                insert_term_param = {'term': term, 'num_chars': str(len(term))}

                cur.execute(insert_term_query, insert_term_param)

    # 4 Update the index
    # 4.1 Find all terms that belong to the document
    # 4.2 Create a data structure the stores how many times (count) each term appears in the document
    # 4.3 Insert the term and its corresponding count into the database
    # --> add your Python code here
        term_count = {}
        for term in terms:
            term_count[term] = 1 + term_count.get(term, 0)

        for term, term_count in term_count.items():
            insert_index_query = "INSERT INTO Index (term, doc, term_count) VALUES (%(term)s, %(doc)s, %(term_count)s)"
            insert_index_param = {'term': term, 'doc': docId, 'term_count': term_count}

            cur.execute(insert_index_query, insert_index_param)

    except Exception as e:
        print("Create document error: " + str(e))
        

def deleteDocument(cur, docId):

    # 1 Query the index based on the document to identify terms
    # 1.1 For each term identified, delete its occurrences in the index for that document
    # 1.2 Check if there are no more occurrences of the term in another document. If this happens, delete the term from the database.
    # --> add your Python code here
    get_doc_query = "SELECT * FROM Documents WHERE Documents.doc = %(docId)s;"
    get_doc_param = {'docId': docId}

    cur.execute(get_doc_query, get_doc_param)

    doc_result = cur.fetchall()

    # If the sql results nothing -> invalid doc id
    if len(doc_result) == 0:
        print("Invalid doc id")
        return
    
    # 2 Delete the document from the database
    # --> add your Python code here
    delete_index_query = "DELETE FROM Index WHERE Index.doc = %(docId)s;"
    delete_index_param = {'docId': docId}

    delete_doc_query = "DELETE FROM Documents WHERE Documents.doc = %(docId)s;"
    delete_doc_param = {'docId': docId}

    cur.execute(delete_index_query, delete_index_param)
    cur.execute(delete_doc_query, delete_doc_param)


def updateDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Delete the document
    # --> add your Python code here
    deleteDocument(cur, docId)

    # 2 Create the document with the same id
    # --> add your Python code here
    createDocument(cur, docId, docText, docTitle, docDate, docCat)


def getIndex(cur):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    # --> add your Python code here

    get_index_query = "SELECT * FROM Index;"
    cur.execute(get_index_query)

    indexes = cur.fetchall()

    get_term_query = "SELECT Terms.term FROM Terms ORDER BY term ASC;"
    cur.execute(get_term_query)

    terms = cur.fetchall()
    inverted_index = {}

    for term in terms:

        # Get corresponding index from every term
        current_index = list(filter(lambda index: index[0] == term[0], indexes))

        term_occurence = []

        if len(current_index) > 0:
            for term, doc, term_count in current_index:
                get_doc_query = "SELECT Documents.title FROM Documents WHERE Documents.doc = %(docId)s;"
                get_doc_param = {'docId': str(doc)}

                cur.execute(get_doc_query, get_doc_param)

                doc_title = cur.fetchall()[0][0]

                # Add document's title with the corresponding term_count from that title
                term_occurence.append((doc_title, term_count))

            # Sort in alphabetical order
            term_occurence.sort(key = lambda occurence: occurence[0])
            term_occurence = list(enumerate(term_occurence))

            inverted_index_value = ""

            # Create value format "<title>:<term_count>" for inverted_index
            for i, occurence in term_occurence:
                inverted_index_value += occurence[0] + ":" + str(occurence[1])
                
                # Addd comma in between
                if i != len(term_occurence)-1 :
                    inverted_index_value += ", "

            # Add value to is corresponding key (term) in inverted_index 
            inverted_index[term] = inverted_index_value

    return inverted_index

