import nltk
import re
from collections import Counter


def make_ngrams(text, n):
    sents = nltk.sent_tokenize(text)
    word = re.compile(r"[\w']+")
    for s in sents:
        words = [w.lower() for w in word.findall(s)]
        ngrams = nltk.util.ngrams(words, n)
        for ngram in ngrams:
            yield " ".join(ngram)

def make_ngram_counts(ngrams):
    return Counter(ngrams)