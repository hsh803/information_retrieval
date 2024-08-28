# information_retrieval
- Assignments notes from Information Retrieval course from Language Technology Mater's program, Uppsala university

## 1. Inverted index (with short texts)
- Implemente following tasks: prepocessing texts (words cleanup, using stop words), creating inverted index of the texts

### Data (from Beloucif M., Sjons J.)
- Starter code: inverted_index.py
- documents(raw texts) 

## 2. Inverted index (with documents files)
- Develope the code of inverted_index.py implemented at step 1. (inverted_index_doc.py)
- Implement following tasks: add functinos to load/read document files, use nltk() library to add functions for preprocessing texts(normalizing, lemmatizing)

## 3. Spelling check Implementation using the Noisy Channel Model
- Implement following tasks: counting ngrams (unigram, bigram, trigram) in the corpus data and convert them into probabilities, generating candidates and listing them using vocabualry data, generating and estimating probabilities of spelling variations of a given word.

### Data (from Beloucif M., Sjons J.)
- Starter code: spell_check.py
- big.txt (Corpus)
- vocab.csv (English Vocab with almost 6000 words)

## 4. Build a mini-search engine
- Develop the code of inverted_index_doc.py implemented at step 2. (query_doc_search.py)
- Add following functions
1) BM25 (query, set of documents): returns a score per document (use BM25 Okapi, https://pypi.org/project/rank-bm25/),
2) TF-IDF (query, set of documents): returns a score (use tf-idf implementation of Scikit, https://melaniewalsh.github.io/Intro-Cultural-Analytics/05-Text-Analysis/03-TF-IDF-Scikit-Learn.html)
3) Call spell_checker.py
4) Query function: returns a list of documents as the results of bm25 and tf-idf of the query. Returns the best document that represents the query using BM25. (Every query has to be spell-checked and normalized before querying to match the terms in the index.)
  
