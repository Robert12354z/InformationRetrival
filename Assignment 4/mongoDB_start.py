#-------------------------------------------------------------------------
# AUTHOR: Roberto Reyes
# FILENAME: mongoDB_start.py
# SPECIFICATION: This program builds an inverted index from a set of documents and stores it in a MongoDB database. The program preprocesses the documents, builds the inverted index, and stores the terms and documents in the database.
# TIME SPENT: 6 hours
#-----------------------------------------------------------*/

import pymongo
import re # Regular expressions
from collections import Counter
from math import log

# Database setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["inverted_index"]
terms_collection = db["terms"]
documents_collection = db["documents"]

# Documents
documents = [
    "After the medication, headache and nausea were reported by the patient.",
    "The patient reported nausea and dizziness caused by the medication.",
    "Headache and dizziness are common effects of this medication.",
    "The medication caused a headache and nausea, but no dizziness was reported.",
]

# Step 1: Preprocessing
def preprocess(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Lowercase all text
    tokens = text.split()  # Tokenize by whitespace
    unigrams = tokens
    bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)]
    return unigrams + bigrams + trigrams

# Step 2: Build Inverted Index

def build_inverted_index(documents):
    vocab = {}
    inverted_index = {}
    document_tf = []
    document_lengths = []

    for doc_id, content in enumerate(documents):
        tokens = preprocess(content)
        tf = Counter(tokens)
        document_tf.append(tf)
        document_lengths.append(sum(tf.values()))

        for term, freq in tf.items():
            if term not in vocab:
                vocab[term] = len(vocab) + 1  # Position in vocabulary
            if term not in inverted_index:
                inverted_index[term] = []
            inverted_index[term].append({"doc_id": doc_id, "tf": freq})

    # Compute TF-IDF
    num_docs = len(documents)
    for term, postings in inverted_index.items():
        df = len(postings)
        idf = log(num_docs / df)
        for entry in postings:
            tf_idf = (entry["tf"] / document_lengths[entry["doc_id"]]) * idf
            entry["tf_idf"] = tf_idf

    return vocab, inverted_index

#Step 3: Insert into MongoDB
def store(vocab, inverted_index, documents):
    terms_collection.delete_many({})
    documents_collection.delete_many({})

    for term, postings in inverted_index.items():
        terms_collection.insert_one({"_id": vocab[term], "term": term, "postings": vocab[term], "docs": postings,})

    for doc_id, content in enumerate(documents):
        documents_collection.insert_one({"_id": doc_id, "content": content})


if __name__ == "__main__":
    vocab, inverted_index = build_inverted_index(documents)
    store(vocab, inverted_index, documents)
    print("Stored in MongoDB")