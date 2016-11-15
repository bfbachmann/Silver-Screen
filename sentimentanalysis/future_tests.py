"""

from app.sentimentanalysis import TweetSentiment
from django.test import TestCase

class TestTweetSentimentIncludedScore(TestCase):
    \"""
    This tests the included_score method (yet to be implemented), which will decipher
    an inclued score if the twitter user has rated a movie within the tweet.
    1. Standard tweet whose score agrees with the sentiment
    2. Odd case where positive sentiment and bad score
    3. Odd case where negative sentiment and positive score
    4. Testing whether irregular scoring systems (*/4) are accounted for
    5. Testing whether float numbers are accepted correctly
    6. Natural language processing of an input ("5 stars" = 5/5 = 1.00)
    7. Similarly, if people use "out of" instead of "/"
    8. If people waver, tests whether we take an average of two scores.
    \"""
    def test_included_score(self):
        test1 = "Loved this movie. 8/10"
        test2 = "Great movie. 2/10"
        test3 = "Terrible movie. 10/10"
        test4 = "Wonderful film, I loved it. 3/4"
        test5 = "This was a movie, and I saw it. 2.5/5"
        test6 = "I'd give this movie 5 stars"
        test7 = "Honestly, this film is like a 5 out of 10"
        test8 = "if you ask me, this movie is a 3 or a 4"

        self.assertEqual(TweetSentiment.included_score(test1), 0.80)
        self.assertEqual(TweetSentiment.included_score(test2), 0.20)
        self.assertEqual(TweetSentiment.included_score(test3), 1.00)
        self.assertEqual(TweetSentiment.included_score(test4), 0.75)
        self.assertEqual(TweetSentiment.included_score(test5), 0.50)
        self.assertEqual(TweetSentiment.included_score(test6), 1.00)
        self.assertEqual(TweetSentiment.included_score(test7), 0.50)
        self.assertEqual(TweetSentiment.included_score(test8), 0.35)

"""
