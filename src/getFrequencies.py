import requests
import json
import re
import numpy as np
import shelve

#constants
start_year = 1800 #before this year the dataset is pretty sparse
end_year = 1999
years = [i for i in range(start_year, end_year+1)]
call_limit = 10 # how many ngrams can be called at once

#the api takes a number from which it draws the ngram counts
class Corpus(object):
    english = 15

#the shelf is a way to cache the ngram results so that the api does not need to be
#called for everything
def load_shelf(n, corpus):
    return shelve.open("../caches/cache_corpus_{}_n_{}".format(corpus, n))


def process_raw_data(ngrams, raw_data):
    data = []
    for ngram in ngrams:
        #since it is a case insenstive search there could be multiple results per ngram
        matches = [n for n in raw_data if (n["ngram"].lower() == ngram + " (all)") or
                                          (n["type"] == "NGRAM" and n["ngram"].lower() == ngram)]
        if len(matches) > 0:
            array = np.float_(matches[0]['timeseries'])
        else:
            array = np.float_([0.0 for i in range(end_year - start_year + 1)])
        data.append(array)
    return data


def make_totals(corpus):
    raw_counts = file("../metadata/{}_counts.txt".format(corpus)).read()
    totals = []
    for year_count in raw_counts.split("\t"):
        items = year_count.split(",")
        if int(items[0]) in years:
            totals.append(int(items[1]))
    return np.float_(totals)

def call_api(ngrams, corpus, smoothing, cache):
    params = {"content": ",".join(ngrams),
              "case_insensitive": "on",
              "year_start": start_year,
              "year_end": end_year,
              "corpus": corpus,
              "smoothing": smoothing}

    req = requests.get('http://books.google.com/ngrams/graph', params=params)
    req.raise_for_status()
    result = re.findall('var data = (.*?);\\n', req.text)
    if not result:
        cache.close()
        raise Exception("API response not as expected")
    raw_data = json.loads(result[0])
    return process_raw_data(ngrams, raw_data)


def call_group(ngrams, corpus, smoothing, cache):
    results = call_api(ngrams, corpus, smoothing, cache)
    for ngram, result in zip(ngrams, results):
        cache[ngram] = result
    return results


def get_ngram_counts(n, ngrams, smoothing=0, corpus=Corpus.english):
    cache = load_shelf(n, corpus)
    data = []
    totals = make_totals(corpus)
    to_call = []
    for ngram in ngrams:
        if cache.has_key(ngram):
            data.append(cache[ngram])
        else:
            to_call.append(ngram)
        if len(to_call) == call_limit:
            data += call_group(to_call, corpus, smoothing, cache)
            to_call = []

    if len(to_call) > 0:
        data += call_group(to_call, corpus, smoothing, cache)

    cache.close()
    return data, totals


