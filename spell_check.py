import re
import collections
import csv
from string import punctuation as PUNKT


class LMC:
    '''
        Class for loading data, tokenizing, generating ngram probabilities, and 
        generating spell check canditates.
    '''
    def __init__(self, corpus=None, vocab=None, order=3) -> None:
        '''
            Constructor for model. 
            order -> n-gram setting
            _count -> dict of dicts containing ngram counts
            _prob -> dict of dicts containing ngram probabilities
            vocab -> set of english words
        '''
        self.order = order
        self._count = None
        self._prob = None
        self.vocab = set()
        # if a corpus or vocab is provided in the constructer parameters
        # we use that, otherwise we have to manually call the functions
        if corpus is not None:
            self.train(corpus)
        if vocab is not None:
            self.vocab = vocab

        
    def load_corpus_from_txt(self, path):
        '''
            load the corpus from file path and
            train the model on the data
        '''
        #TODO1: load corpus from file
        # My comment: Assign text lines from big.txt file to corpus variable
        with open(path, "r") as file:
            corpus = file.readlines()        
        
        self.train(corpus)

    def load_vocab_from_csv(self, path):
        '''
            load vocab from path (csv file)
            and turn it into a set()
        '''
      #TODO2: load the vocab from the csv file
      # My comment: Add uniq words to vocab variable by reading all words from vocab.csv file
        with open(path) as file: 
            for word in file.readlines():
                self.vocab.add(word.strip("\n"))
        

    def extend_vocab_from_corpus(self):
        '''
            the vocab file is pretty small, so with this
            method we can extend it with the data from the 
            corpus.
        '''
        for key in self._count[1].keys():
            self.vocab.add(key[0])

    def train(self, corpus):
        '''
            method to count ngrams in the corpus data and convert them into probabilities
        '''
        # instanciate the dictionaries for counts and probabilities, one entry for each
        # order of the model
        self._count = {ord: collections.defaultdict(int) for ord in range(1, self.order+1)}
        self._prob = {ord: collections.defaultdict(float) for ord in range(1, self.order+1)}
        self.N = 0 # total number of tokens in the corpus

        for line in corpus:
            tokens = self.tokenize(line)
             #TODO3  add the number of tokens in the sentence to the 
             # to the total before modifying the list
             # My comment: Add the number of tokens in each text line from corpus 
            self.N += len(tokens)
            if len(tokens): # if the list is not empty
                # we add some dummy tokens in the beginning of the sentence to 
                # normalize the length of the keys in the dictionary
                tokens = ['<SOS>' for _ in range(self.order)] + tokens
                
                # TODO4 BELOW: looping through the indices of the tokens list
                # and the orders of the models, here you create all ngrams from 
                # 1-gram to n-gram.
                # My comment: Each ord contain n-order word(tuple) as key and its frequenct(int) as value 
                for i in range(len(tokens)):
                    for ord in range(1, self.order + 1):
                        self._count[ord][tuple(t for t in tokens[i:i+ord])] += 1
            # because we are adding more <SOS> tokens in the higher order models we 
            # will end up with an inflated number of <SOS> tokens in the lower n-grams
            # so we remove the excess by setting the number of <SOS> to the number in 
            # our highest order n-gram
            for ord in range(1, self.order):
                self._count[ord][tuple('<SOS>' for _ in range(ord))] = \
                self._count[self.order][tuple('<SOS>' for _ in range(self.order))]

        # for each order of n-gram we calculate the probablities of all of the 
        # ngrams
        for ord in range(1, self.order + 1):
            for key in self._count[ord].keys():
                #TODO5
                # My comment: Count n-order word for calculating probability 
                if len(key) == 1:
                    self._prob[ord][key] = self.word_count(key)/self.N
                    
                elif len(key) > 1:
                    self._prob[ord][key] = self.word_count(key)/self.word_count(key[:len(key)-1])
     
    def tokenize(self, line):
        '''
            simple tokenization method where we 
            add spaces between punctuation and words and split 
            it using white space
        '''
        for c in PUNKT:
            line = line.lower().replace(c, f' {c} ')
        return [t for t in line.split() if t]
    
    def word_prob(self, ngram):
        '''
            depending on the length of the ngram tuple
            we access different dictionaries for different
            n-gram probabilites
        '''
        if isinstance(ngram, str):
            ngram = (ngram,)
        assert isinstance(ngram, tuple)
        ord = len(ngram)
        return self._prob[ord][ngram]
    
    def word_count(self, ngram):
        '''
            works the same way as the word_prob function
            but accesses the word count dictionaries instead
        '''
        if isinstance(ngram, str):
            ngram = (ngram,)
        assert isinstance(ngram, tuple)
        ord = len(ngram)
        return self._count[ord][ngram]

    def generate_candidates(self, word):
        '''
            method to generate all of the edit distance 1 candidates
        '''
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        # a list of all split permutations of the word -> boat, b oat, bo at, boa t, boat
        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        # for each split-pair, remove the first letter in the right split and concatenate 
        deletes    = [L + R[1:] for L, R in splits if R]
        # TODO0 FINISH the below permutations
        # swap the positions of the first two characters in of the right split
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1] 
        # replace the first character of the right split with every letter in the 
        # alphabet
        replaces   = [L + j + R[1:] for L, R in splits if len(R) > 0 for j in letters]
        # insert every letter of the alphabet between the left and right
        # split
        inserts    = [L + j + R for L, R in splits for j in letters]
        candidates = set(deletes + transposes + replaces + inserts)
        # create a list from the intersect of the candidates and the real words
        # in the vocabulary
        return list(candidates.intersection(self.vocab))

    def spell_correction(self, sent, order=None):
        '''
            method for generating and estimating probabilities of spelling
            variations of a word. It traverses the sentence from left to 
            right since the probabilities of each correction only depends
            on the prior words.
        '''
        # we are able to set the order to any order lower than the
        # order our model is trained at.
        if order == None or order > self.order:
            order = self.order
        # just like under training, we add some more dummy tokens to facilitate
        # dictionary key generation.
        sent = ['<SOS>' for _ in range(self.order - 1)] + self.tokenize(sent)
        # instantiate a list for the spell corrected sentence
        corrected = []
        # we loop through the sentence
        for i, word in enumerate(sent):
            # we instantiate a list for probabilities of the candidates
            probabilities = []
            # if the word is not a dummy token and if the word is not a word 
            # in the vocabulary
            if word != '<SOS>' and word not in self.vocab:
                # first we append the orignal word and its probability so that the list
                # is not empty
                current_word = (word,
                             self.word_prob((tuple([corrected[j] for j in range(i-(order-1), i)] + [word]))))
                probabilities.append(current_word)
                # we generate the candidates
                candidates = self.generate_candidates(word)
                # for each candidate we calculate its probability and append it to the probabilities list
                # which we then sort.
                for cand in candidates:
                    prob = self.word_prob((tuple([corrected[j] for j in range(i-(order-1), i)] + [cand])))
                    probabilities.append((cand, prob))
                probabilities = sorted(probabilities, key=lambda a:a[1], reverse=True)
                # we add the best candidate to the list of corrected words
                if probabilities[0][0] == word:
                    print(f"Could not find correct spelling for '{probabilities[0][0]}'.")
                else:
                    print(f"Correction: '{word}' -> '{probabilities[0][0]}'.")
                corrected.append(probabilities[0][0])
            else:
                if word != '<SOS>':
                    print(f"'{word}' is spelled correctly.")
                # if the word is a real word or <SOS> we just append it to the corrected
                corrected.append(word)
        # we remove the <SOS> slice and join it with white space
        return ' '.join(corrected[self.order-1:])


def main():

    # n-gram order
    order = 3

    # we instanciate the Noisy Channel Model
    # and load the corpus, vocab and extend the
    # vocab list with the corpus data
    lm = LMC(order=order)
    lm.load_corpus_from_txt('big.txt')
    lm.load_vocab_from_csv('vocab.csv')
    #lm.extend_vocab_from_corpus()
    
    
    # Get user input
    while True:
        user_in = input('Enter a word to spell-check (or "quit()" to exit): ')
        if user_in == 'quit()':
            break
        
        # spell check using adjustable n-gram orders
        print(lm.spell_correction(user_in, order=order))

if __name__ == '__main__':
    main()
