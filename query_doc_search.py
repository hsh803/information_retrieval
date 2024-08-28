#!/usr/bin/env python

from functools import reduce
import unicodedata
import glob
import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer 
import spell_check
####################   This here is your input data #####################
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

doc1 = """                                                                                                                                                                       
Situated on the fertile Uppsala flatlands of muddy soil, the city features the small Fyris River flowing through the landscape surrounded by lush vegetation.
Parallel to the river runs the glacial ridge of Uppsalasen at an elevation around 30m, the site of Uppsala's castle, from which large parts of the town can be seen.
"""

doc2 = """                                                                                                                                                                       
Uppsala University (Swedish: Uppsala universitet) is a public research university in Uppsala, Sweden.
Founded in 1477, it is the oldest university in Sweden and the Nordic countries still in operation.

The university rose to significance during the rise of Sweden as a great power at the end of the 16th century and was then given relative financial stability with a large donation from King Gustavus Adolphus in the early 17th century. Uppsala also has an important historical place in Swedish national culture, and identity and for the Swedish establishment: in historiography, literature, politics, and music. 
"""


###############         End data ########################################



_WORD_MIN_LENGTH = 2   #change, and explain why? I chnage from 0 to 2 to clean up words that are less than 2 in length. 

_STOP_WORDS = frozenset(['and', 'the', 'are', 'can', 'this', 'that'])  #what does that do? To complete cleaning word that couldn't with min length method above. 



def split_the_words(text):
    #### TODO 2: What does this do? Creating a list where we store all words with unique key.
    """
    TODO2 : What does this function do, what is returned? Give an example. 
    """
    word_list = []
    current_word = []
    index_word = None

    for i, c in enumerate(text): # what does enumerate do?? What's the difference between read and enumerate? Read takes text as a whole text while enumerate add a counter to each character in each iteration.
        if c.isalnum(): # What is isalnum do? Return if all characters are alphanumeric, otherwise False. 
            current_word.append(c)  # Explain every part of this, If a character is an alphanumeric, add it to the list of current_word
            index_word = i # Assign its counter to this variable.
        elif current_word:
            word = u''.join(current_word) ## why do we have a u in here? It indicates that the joined string is a Unicode.
            word_list.append((index_word - len(word) + 1, word))
            current_word = []
    if current_word:
        word = u''.join(current_word)
        word_list.append((index_word - len(word) + 1, word))   ### There seems to be two things appended, what are those?? I think the last if statement can be removed.  
    return normal_lemma(word_list) # return word_list not to preprocess it, which gives the length of inverted index, 8429. Using normal_lemma function for preprocessing, gives the lenght of the index, 6782.


def words_cleanup(words):
    """
    Remove words with length less then a minimum and stopwords.
  
    """
    cleaned_words = []
    for index, word in words:
        #TODO 3: Complete this function!!!!
        ## Write the cleaning up, is there anything changing in the outcome? What and Why? The words that are less than 3 in length are removed from the original list of words.
        if len(word) > _WORD_MIN_LENGTH and word not in _STOP_WORDS:
            cleaned_words.append((index, word))    
    return cleaned_words

def word_preprocess(text):
    """
    Just a helper method to process a text.
    What does it do?? 
    """
    words = split_the_words(text)
    words = words_cleanup(words) #(this has to be commented out after the cleanup function is fully written)
    return words

def normal_lemma(words):
    lemmatizer = WordNetLemmatizer()
    be = ["am", "are", "is", "was", "were"]
    new_word_list = []
    for token in words:
        token = list(token)
        t = token[1].lower()
        if t in be:
            t = "be"
        else:
            t = lemmatizer.lemmatize(t)
        token[1] = t
        token = tuple(token)
        new_word_list.append(token)
    return new_word_list

def inverted_index(text): #TODO 3: What does this function help with???
    """
   Describe what does this do?
    """
    inverted = {}

    for index, word in word_preprocess(text):
        locations = inverted.setdefault(word, [])
        locations.append(index)
        #Print the outcome of this function and analyze what does setdefault do!
    return inverted # what is being returned here? it returns a set of words and corresponding indice in key-value pair.

def inverted_index_add(inverted, doc_id, doc_index):
    """
    Add Invertd-Index doc_index of the document doc_id to the 
    Multi-Document Inverted-Index (inverted), 
    using doc_id as document identifier.
        {word:{doc_id:[locations]}}
    """
    for word, locations in doc_index.items():
          #TODO4: implement the inverted index, it has to return the above information in the comment of the function
       if word in inverted:
           inverted[word].update({doc_id: locations}) # or inverted[word][doc_id] = locations
       else:
            inverted[word] = {doc_id: locations}
    return inverted  #Explain what the difference between this function and the one before!!! inverted_index created a dictionary where we store each token with its all indice while inverted_index_add add doc1 or doc2 to each word with its all indice.

def query_check(query):
    query = query.split()
    lemmatizer = WordNetLemmatizer()
    be = ["am", "are", "is", "was", "were"]
    new_query = []
    for word in query:
        if word in be:
            word = "be"
        else:
            word = lemmatizer.lemmatize(word)
        new_query.append(word)
    return new_query

def bm25(doc_title, doc_text, query):
    bm25 = BM25Okapi(doc_text)
    doc_scores = bm25.get_scores(query)
    scored = {}
    for i in range(len(doc_title)):
        scored[doc_title[i]] = doc_scores[i]
    print(scored)
    best_doc = bm25.get_top_n(query, doc_text, n=1)
    print("Best document: ", doc_title[doc_text.index(best_doc[0])])

def tf_idf(files, titles, query):
    tfidf_vectorizer = TfidfVectorizer(input='filename')
    tfidf_vector = tfidf_vectorizer.fit_transform(files)
    tfidf_data = pd.DataFrame(tfidf_vector.toarray(), index=titles, columns=tfidf_vectorizer.get_feature_names_out())
    tfidf_query = tfidf_data[query]
    print(tfidf_query)

if __name__ == '__main__':

   
    # This line builds Inverted-Index for documents
    inverted = {}
    #documents = {'doc1':doc1, 'doc2':doc2} #what data structure is this? dictionary
    documents = {}
    files = glob.glob('/home/haha/IR/lab2/*.txt') # file path where the documents are placed
    for file in files:
        f = file.split("/")[-1]
        documents[f] = open(f'/home/haha/IR/lab2/{f}', "r").read()
    
    doc_title = []
    doc_text = []

    for doc_id, text in documents.items():
        doc_index = inverted_index(text) #what does this return? dictionary
        doc_title.append(doc_id)
        doc_text.append([w for w in doc_index.keys()])
        inverted_index_add(inverted, doc_id, doc_index) 
    query = query_check(spell_check.main()) 
    bm25(doc_title, doc_text, query)
    # TODO 1: Print Inverted-Index
    #print(inverted, len(inverted)) # Before preprocessing, the length of the index is 8429, after 6782, which means that the preprocessing reduces the length of the index.
    #query_check(spell_check.main())
    tf_idf(files, doc_title, query)
