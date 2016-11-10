from unittest import TestCase
from sentimentanalysis.analyzer import TweetSentiment


class TestTweetSentiment(TestCase):

    def test_polarity_scores(self):
        #tests contains_but
        t_a = TweetSentiment("I hate Michael Bay films, but this one rules love it best sublime superb")
        #tests normal polarity score
        t_a2 = TweetSentiment("I hate Michael Bay films")

        self.assertEqual(t_a.polarity_scores()['sentiment'], 0.9578)
        self.assertEqual(t_a2.polarity_scores()['sentiment'], -0.5719)

    def test_capitalized(self):
        self.assertEqual(TweetSentiment.capitalized(['WHAT', 'ARE', 'WE', 'DOING']), False)
        self.assertEqual(TweetSentiment.capitalized(["What", "ARE", "we", "DOING"]), True)
        self.assertEqual(TweetSentiment.capitalized(["what", "are", "we", "doing"]), False)

    def test__contains_least(self):
        # tests least
        t_a = TweetSentiment("The least good movie")
        t_a2 = TweetSentiment("at the very least, it's a good movie")
        t_a3 = TweetSentiment("at least its a good movie")

        self.assertEqual(t_a._contains_least(1.9, ['The', 'least', 'good', 'movie'], 2), -1.9)
        self.assertEqual(t_a2._contains_least(2.35, ['at', 'the', 'very', 'least', 'it\'s', 'good', 'movie'], 5), 2.35)
        self.assertEqual(t_a3._contains_least(1.9, ['at', 'least', 'it\'s', 'good', 'movie'], 3), 1.9)

    def test_negate(self):
        test1 = "I don't like it"
        test2 = "I do like it"
        test3 = "It aint a good movie"
        test4 = "This is the least good movie ever"
        test5 = "I mean at least its a good movie"

        self.assertEqual(TweetSentiment.negate(test1.split(' ')), True)
        self.assertEqual(TweetSentiment.negate(test2.split(' ')), False)
        self.assertEqual(TweetSentiment.negate(test3.split(' ')), True)
        self.assertEqual(TweetSentiment.negate(test4.split(' ')), True)
        self.assertEqual(TweetSentiment.negate(test5.split(' ')), False)

    def test__exclamation_boost(self):
        test1 = "OMG I can't believe it!"
        test2 = "OMG I can't believe it!!"
        test3 = "This movie rules!!!!!!"

        self.assertEqual(TweetSentiment._exclamation_boost(test1), 0.25)
        self.assertEqual(TweetSentiment._exclamation_boost(test2), 0.50)
        self.assertEqual(TweetSentiment._exclamation_boost(test3), 1.00)

    def test__question_boost(self):
        test1 = "Isn't this movie total crap"
        test2 = "Isn't this movie total crap??"
        test3 = "Isn't this movie total crap???"
        test4 = "Isn't this movie total crap????"

        self.assertEqual(TweetSentiment._question_boost(test1), 0)
        self.assertEqual(TweetSentiment._question_boost(test2), 0.20)
        self.assertEqual(round(TweetSentiment._question_boost(test3), 2), 0.30)
        self.assertEqual(TweetSentiment._question_boost(test4), 1.00)

    def test__organize_scores(self):
        test1 = [2, 3, 2, 5]
        test2 = [-2, -3, -2, -5]
        test3 = [2, -3, 2, -5]
        test4 = [2, 0, -3, 0, 2, -5]

        self.assertEqual(list(TweetSentiment._organize_scores(test1)), [12.0, 0.0, 0])
        self.assertEqual(list(TweetSentiment._organize_scores(test2)), [0.0, -12.0, 0])
        self.assertEqual(list(TweetSentiment._organize_scores(test3)), [4.0, -8.0, 0])
        self.assertEqual(list(TweetSentiment._organize_scores(test4)), [4.0, -8.0, 2])

    def test_normalize(self):
        test1 = 20
        test2 = -20
        test3 = 15
        test4 = -15
        test5 = 3
        test6 = 0

        self.assertEqual(round(TweetSentiment.normalize(test1), 4), .9818)
        self.assertEqual(round(TweetSentiment.normalize(test2), 4), -.9818)
        self.assertEqual(round(TweetSentiment.normalize(test3), 4), .9682)
        self.assertEqual(round(TweetSentiment.normalize(test4), 4), -.9682)
        self.assertEqual(round(TweetSentiment.normalize(test5), 4), .6124)
        self.assertEqual(round(TweetSentiment.normalize(test6), 4), 0.0)

    def test__words_and_symbols(self):
        t_a1 = TweetSentiment("I hate Michael Bay films, but this one rules love it best sublime superb")
        t_a2 = TweetSentiment("I htae Michael bay films, and this one scks")
        t_a3 = TweetSentiment("I never loved it")
        t_a4 = TweetSentiment("1 2 3 4")
        t_a5 = TweetSentiment("Never have we so loved a movie")

        self.assertEqual(t_a1.words_and_symbols, ['hate', 'Michael', 'Bay', 'films', 'but', 'this', 'one', 'rules', 'love', 'it', 'best', 'sublime', 'superb'])
        self.assertEqual(t_a2.words_and_symbols, ['htae', 'Michael', 'bay', 'films', 'and', 'this', 'one', 'scks'])
        self.assertEqual(t_a3.words_and_symbols, ['never', 'loved', 'it'])
        self.assertEqual(t_a4.words_and_symbols, [])
        self.assertEqual(t_a5.words_and_symbols, ['Never', 'have', 'we', 'so', 'loved', 'movie'])
