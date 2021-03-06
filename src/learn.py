from makeNgrams import make_ngrams, make_ngram_counts
import numpy as np
from scraper import Corpus, NgramScraper



class Learner(object):

    #arguments:
    #   start_year - the first year to get ngram data from, note that the earlier it is, the less data
    #   end_year - the last year to get ngram data from, inclusive note that the latest year possible is corpus dependant
    #   bucket_length - how large is bucket is
    #   psuedocount  - the value added to the yearly totals, should not be 0 or else some years
    #                   will not be considered due to 0 occurances in the corpus in that year
    def __init__(self, start_year=1800, end_year=1999, bucket_length=10, psuedocount=1):
        self.start_year = start_year
        self.end_year = end_year
        self.bucket_length = bucket_length
        self.psuedocount = psuedocount

    def make_start_years(self):
        return np.int_(xrange(self.start_year, self.end_year + 2 - self.bucket_length, self.bucket_length))

    def make_buckets( self, freqs, totals):
        start_years = self.make_start_years()
        counts = freqs * totals
        #need to normalize to adjust for the fact that the years have wildly different total counts
        adjust_factors = np.float_(totals.max()) / totals
        final_counts = (counts * adjust_factors) + self.psuedocount
        final_probs = final_counts / final_counts.sum()
        buckets = np.float_([final_probs[start:start+self.bucket_length].sum()
                                    for start in start_years - self.start_year])
        return buckets


    #parameters:
    #   text - the text to be analyzed
    #   n - how many words make up 1 ngram, note that the maximum value depends on the corpus
    #   amount - how many ngrams go into the date calculation, note this exists because calling the api
    #           is slow so lower values mean less ngrams to lookup
    def predict_year(self, text, n, amount, corpus=Corpus.english):
        ns = NgramScraper(n, corpus)
        counts = make_ngram_counts(make_ngrams(text, n))
        most_common = counts.most_common(amount)
        common_ngrams = [a for a,b in most_common]
        common_counts = [b for a,b in most_common]
        frequencies = ns.get_ngram_counts(common_ngrams)
        totals = ns.make_totals()
        years = self.make_start_years()
        processed = [np.log(self.make_buckets(f, totals)) for f in frequencies]
        final_prob = np.zeros(processed[0].size)
        for p, c in zip(processed, common_counts):
            final_prob += p*c

        return [b for a,b in sorted(zip(final_prob, years), key=lambda x:x[0], reverse=True)]


