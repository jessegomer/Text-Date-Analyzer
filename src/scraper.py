import requests
import json
import re
import numpy as np
import shelve

class Corpus(object):
    english = 15


class NgramScraper(object):
    def __init__(self, n, corpus=Corpus.english, smoothing=0,  start_year=1800, end_year=1999, call_limit=10):
        self.start_year = start_year
        self.end_year = end_year
        self.years = [i for i in range(start_year, end_year+1)]
        self.range = len(self.years)
        self.n = n
        self.corpus = corpus
        self.smoothing = smoothing
        self.call_limit = call_limit

    def load_shelf(self):
        return shelve.open("../caches/cache_corpus_{}_n_{}".format(self.corpus, self.n))

    def process_raw_data(self, ngrams, raw_data):
        data = []
        for ngram in ngrams:
            #since it is a case insenstive search there could be multiple results per ngram
            matches = [n for n in raw_data if (n["ngram"].lower() == ngram + " (all)") or
                                              (n["type"] == "NGRAM" and n["ngram"].lower() == ngram)]
            if len(matches) > 0:
                array = np.float_(matches[0]['timeseries'])
            else:
                array = np.zeros(self.range, np.float_)
            data.append(array)
        return data

    def make_totals(self):
        raw_counts = file("../metadata/{}_counts.txt".format(self.corpus)).read()
        totals = []
        for year_count in raw_counts.split("\t"):
            items = year_count.split(",")
            if int(items[0]) in self.years:
                totals.append(int(items[1]))
        return np.float_(totals)

    def call_api(self, ngrams, cache):
        params = {"content": ",".join(ngrams),
                  "case_insensitive": "on",
                  "year_start": self.start_year,
                  "year_end": self.end_year,
                  "corpus": self.corpus,
                  "smoothing": self.smoothing}

        req = requests.get('http://books.google.com/ngrams/graph', params=params)
        req.raise_for_status()
        result = re.findall('var data = (.*?);\\n', req.text)
        if not result:
            cache.close()
            raise Exception("API response not as expected")
        raw_data = json.loads(result[0])
        return self.process_raw_data(ngrams, raw_data)

    def call_group(self, ngrams, cache):
        results = self.call_api(ngrams, cache)
        for ngram, result in zip(ngrams, results):
            cache[ngram] = result
        return results

    def get_ngram_counts(self, ngrams):
        cache = self.load_shelf()
        data = []
        to_call = []
        for ngram in ngrams:
            if cache.has_key(ngram):
                data.append(cache[ngram])
            else:
                to_call.append(ngram)
            if len(to_call) == self.call_limit:
                data += self.call_group(to_call, cache)
                to_call = []

        if len(to_call) > 0:
            data += self.call_group(to_call, cache)

        cache.close()
        return data

