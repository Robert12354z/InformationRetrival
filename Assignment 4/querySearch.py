#-------------------------------------------------------------------------
# AUTHOR: Roberto Reyes
# FILENAME: querySearch.py
# SPECIFICATION: This program is a search engine that retrieves documents from a MongoDB database based on a query. The program preprocesses the query and retrieves documents based on the terms in the query.
# TIME SPENT: 6 hours
#-----------------------------------------------------------*/

import pymongo
import re

# Database setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["inverted_index"]
terms_collection = db["terms"]
documents_collection = db["documents"]

# Step 1: Preprocessing
def preprocess(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Lowercase all text
    tokens = text.split()  # Tokenize by whitespace
    unigrams = tokens
    bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)]
    return unigrams + bigrams + trigrams

# Step 2: querySearch

def querySearch(query):
    query_terms = preprocess(query)
    matching_docs = {}

    for term in query_terms:
        varb = terms_collection.find_one({"term": term})
        if varb:
            for doc in varb["docs"]:
                doc_id = doc["doc_id"]
                if doc_id not in matching_docs:
                    matching_docs[doc_id] = 0
                matching_docs[doc_id] += doc["tf_idf"]

    results = []
    for doc_id, score in sorted(matching_docs.items(), key=lambda x: x[1], reverse=True):
        doc = documents_collection.find_one({"_id": doc_id})
        results.append((doc["content"], score))
    
    return results

# Step 3: Query the inverted index

if __name__ == "__main__":

    queries = [("q1", "nausea and dizziness"), ("q2", "effects"), ("q3", "nausea was reported"), ("q4", "dizziness"), ("q5", "the medication")]

    for query_id, query_text in queries:
        results = querySearch(query_text)
        print(f"Query {query_id}: {query_text}")
        for content, score in results:
               print(f'"{content}", {score:.2f}')
        print()

     