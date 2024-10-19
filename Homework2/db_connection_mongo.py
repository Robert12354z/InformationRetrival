#-------------------------------------------------------------------------
# AUTHOR: Roberto Reyes
# FILENAME: db_connection_mongo.py
# SPECIFICATION: This program contains functions to connect to a MongoDB database, create, delete, update documents, and create an inverted index.
# FOR: CS 5180- Assignment #2
# TIME SPENT: 2 hours
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
from pymongo import MongoClient  # import mongo client to connect

def connectDataBase():
 # Connect to the MongoDB server
    client = MongoClient("mongodb://localhost:27017/")
    db = client["assignment2"]  # Name of the database
    return db


def createDocument(col, docId, docText, docTitle, docDate, docCat):

    # Creating the document
    terms = docText.lower().split()
    term_count = {term: terms.count(term) for term in set(terms)}
    document = {
        "_id": docId,
        "text": docText,
        "title": docTitle,
        "date": docDate,
        "category": docCat,
        "terms": term_count
    }
    # Insert the document
    col.insert_one(document)

def deleteDocument(col, docId):

    # Delete the document from the collection by ID
    col.delete_one({"_id": docId})

def updateDocument(col, docId, docText, docTitle, docDate, docCat):

 # Update a document by deleting the old one and inserting a new version
    deleteDocument(col, docId)
    createDocument(col, docId, docText, docTitle, docDate, docCat)

def getIndex(col):
 # Retrieve all documents and create an inverted index
    inverted_index = {}
    documents = col.find()
    
    for doc in documents:
        doc_id = doc["_id"]
        title = doc["title"]
        for term, count in doc["terms"].items():
            entry = f"{title}:{count}"
            if term in inverted_index:
                inverted_index[term] += f", {entry}"
            else:
                inverted_index[term] = entry
    
    return dict(sorted(inverted_index.items()))