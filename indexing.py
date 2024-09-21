#-------------------------------------------------------------------------
# AUTHOR: Roberto Reyes
# FILENAME: indexing.py
# SPECIFICATION: calculate the tf-idf weights for a collection of documents
# FOR: CS 5180- Assignment #1
# TIME SPENT: 6 hours
#-----------------------------------------------------------*/

#Importing some Python libraries
import csv
import math

documents = []



#Reading the data in a csv file
with open( 'collection.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for i, row in enumerate(reader):
         if i > 0:  # skipping the header
            documents.append (row[0])


#Conducting stopword removal for pronouns/conjunctions. Hint: use a set to define your stopwords.

stopWords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours','and', 'her', 'their', 'they','she'])


cleaned_sentences = []

for sentence in documents:
    words = sentence.split()
    filtered_words = [word for word in words if word.lower() not in stopWords]
    cleaned_sentences.append(' '.join(filtered_words))

#print(cleaned_sentences)
  

#Conducting stemming. Hint: use a dictionary to map word variations to their stem.
#--> add your Python code here

stem_mapping = { 'cats': 'cat', 'dogs': 'dog', 'loves': "love"}

stemmed_sentences = []

for sentence in cleaned_sentences:
    words = sentence.split()
    stemmed_words = [stem_mapping.get(word, word) for word in words]
    stemmed_sentences.append(' '.join(stemmed_words))


#Identifying the index terms.
#--> add your Python code here
terms = list()

for sentence in stemmed_sentences:
    words = sentence.split()
    for word in words:
        terms.append(word)


#Building the document-term matrix by using the tf-idf weights.
#--> add your Python code here
docTermMatrix = [[0 for _ in terms] for _ in stemmed_sentences]

for i, sentence in enumerate(stemmed_sentences):
    words = sentence.split()
    total_terms = len(words)
    for word in words:
        if word in words:
            docTermMatrix[i][terms.index(word)] += 1 / total_terms

df = [sum(1 for doc in docTermMatrix if doc[i] > 0) for i in range(len(terms))]

idf = [math.log(len(stemmed_sentences) / df_val) if df_val != 0 else 0 for df_val in df]

tfidf_matrix = [[docTermMatrix[i][j] * idf[j] for j in range(len(terms))] for i in range(len(stemmed_sentences))]

term_dict = {}

for row in tfidf_matrix[1:]:
    term = row[0]
    values = row[1:]

    if term not in term_dict:
        term_dict[term] = values
    else:
        term_dict[term] = [max(term_dict[term][i], values[i]) for i in range(len(values))]

header = tfidf_matrix[0]
consolidated_matrix = [header]

for term, values in term_dict.items():
    consolidated_matrix.append([term] + values)


#Printing the document-term matrix.

col_width = max(len(str(word)) for row in consolidated_matrix for word in row) + 2

for row in consolidated_matrix:
    print("".join(str(word).ljust(col_width) for word in row))