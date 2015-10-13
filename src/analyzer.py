from learn import Learner
#shows an example of usage


text = file("../text/austen/complete.txt").read()
learner = Learner(bucket_length=10)
print learner.predict_year(text, 2, 2000)



