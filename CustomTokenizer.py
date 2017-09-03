'''
=====================================================================================
Custom tokenizer for the TextClassifier
=====================================================================================

This script is part of the supplemental material for the paper "Supervised Text Classification: A Tutorial on Model Selection and Evaluation".
It is a Python script written in Python 3.5.2 on a Windows machine. It can best be viewed using Notepad++, see "README.txt" for more information.
This script does not contain parameters or variables to be set, it only defines the custom tokenizer that is used in the main script (TextClassifier.py).
A full explanation of the tokenization process can be found in the paper.
'''


import nltk
import string
import re

class CustomTokenizer(object):


    def __init__(self, language, do_stemming):
        self.do_stemming = do_stemming
        self.language = language

        if self.do_stemming:
            self.stemmer = nltk.stem.SnowballStemmer(self.language, ignore_stopwords=True)

    def __call__(self, doc):
        text = "".join([ch for ch in doc if ch not in string.punctuation and not ch.isdigit()])
        tokens = nltk.word_tokenize(text, language=self.language)

        if self.do_stemming:
            stemmed = []

            for item in tokens:
                stemmed.append(self.stemmer.stem(item))

            return stemmed
        else:
            return tokens
