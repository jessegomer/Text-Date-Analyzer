This is a tool for trying to determine the date that a text was written based on the ngrams contained in it. It scrapes the Google Books Ngram viewer (https://books.google.com/ngrams) to find the probability that a certain ngram appeared in each year, then does Naive Bayes on those probabilities.   

#####Usage:
To use the demo, call analyzer.py with a filepath as the only argument.

To use it as a library, just import learn.py

Requirements: Python 2.7, Numpy, Requests, NLTK (I recommend using the Anaconda Python distribution)


#####TODO:
- Improve command line interface
- Improve caching performance
- Explore other data sources
- Add new ways of making buckets
- Compare accuracy of parameters
- Test out a different algorithm to help correct systematic flaws in the database. 


Built by Jesse Gomer

Idea by Nick Heindl