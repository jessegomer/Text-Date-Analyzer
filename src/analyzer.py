from learn import Learner
import sys

# This file shows an example of usage

if not len(sys.argv) == 2:
    print "Program must be called with one argument, the filename"

bucket_length = 10
text = file(sys.argv[1]).read()
learner = Learner(bucket_length=bucket_length)
years = learner.predict_year(text, 2, 1000)
print "Most likely year range: {} - {}".format(years[0], years[0] + bucket_length - 1)
