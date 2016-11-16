## =============================================================================
## tests.py
## =============================================================================

from django.test import TestCase
from app.models import *
from datetime import datetime
from datetime import timezone
from sentimentanalysis.analyzer import TweetSentiment
import twitter
import omdb
import json


class TweetTest(TestCase):

    def setUp(self):
        Tweet.objects.create(
                text='Hello world',
                tweetID=1234567,
                created_at=datetime.now(timezone.utc),
                favorite_count=9,
                lang='en',
                location='Russia',
                retweet_count=7,
                user_name='sara',
                user_screen_name='sarita',
                user_verified=True,
                imdbID=57839,
                sentiment_score=0.2647,
            )


    def test_fill_with_valid_status(self):
        current_datetime=datetime.utcnow()
        current_datetime=datetime.now(timezone.utc)
        current_datetime_string=datetime.strftime(current_datetime, '%a %b %d %H:%M:%S +0000 %Y')
        sample_user=twitter.User(
                id=718443,
                name='Kesuke Miyagi',
                screen_name='kesuke',
                location='Okinawa, Japan',
                verified=False,
                lang='ja'
            )
        sample_status=twitter.Status(
                created_at=current_datetime_string,
                id=4391023,
                text=u'wow guys this is a really sick tweet!',
                user=sample_user,
                retweet_count=8,
                favorite_count=0
            )
        sample_status.imdbID = 947502
        tweet=Tweet().fillWithStatusObject(sample_status, 'Random Movie')
        resulting_time = datetime.strftime(tweet.created_at, '%a %b %d %H:%M:%S +0000 %Y')
        expected_time = datetime.strftime(current_datetime, '%a %b %d %H:%M:%S +0000 %Y')

        self.assertEqual(tweet.text, u'wow guys this is a really sick tweet!')
        self.assertEqual(tweet.tweetID, 4391023)
        self.assertEqual(resulting_time, expected_time)
        self.assertEqual(tweet.favorite_count, 0)
        self.assertEqual(tweet.lang, 'ja')
        self.assertEqual(tweet.location, 'Okinawa, Japan')
        self.assertEqual(tweet.retweet_count, 8)
        self.assertEqual(tweet.user_name, 'Kesuke Miyagi')
        self.assertEqual(tweet.user_screen_name, 'kesuke')
        self.assertEqual(tweet.user_verified, sample_user.verified)
        self.assertTrue(tweet.sentiment_score >= -1 and tweet.sentiment_score <= 1)
        self.assertEqual(tweet.imdbID, 947502)


    def test_fill_with_invalid_status(self):
        none_tweet=Tweet().fillWithStatusObject(None, 'Just a Movie')
        self.assertEqual(none_tweet, None)


    def test_fill_with_duplicate_status(self):
        sample_user=twitter.User(
                id=718443,
                name='Bob Loblaw',
                screen_name='bobby',
                location='Vancouver, Canada',
                verified=True
            )
        sample_status=twitter.Status(
                created_at=datetime.strftime(datetime.now(timezone.utc), '%a %b %d %H:%M:%S +0000 %Y'),
                id=1234567,
                text='Hello world',
                user=sample_user,
                retweet_count=1,
                favorite_count=5,
            )
        sample_status.imdbID = 57839
        duplicate_tweet = Tweet().fillWithStatusObject(sample_status, 'Random Movie')

        self.assertEqual(duplicate_tweet, None)


class MovieTest(TestCase):

    def setUp(self):
        pass


    def test_fill_with_valid_movie(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$36,983,927',
                'Director': 'David Blain',
                'Title' : 'The Amazing Race',
                'Year' : 2005,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genres' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatoUserRating' : 6.7,
                'plot' : 'Ben finds love and then his heart gets broken',
                'tomatoConsensus' : 'A coming of age tale of two people in love',
                'Poster' : 'https://resizing.flixster.com/IMveInCaiQgkRrbAq2zPKX_HgYg=/206x305/v1.bTsxMjI0NzMxNjtqOzE3MTUxOzEyMDA7NjE1Ozk2MA',
                'imdbID' : 284957
            }))

        movie = Movie().fillWithJsonObject(raw_movie)

        self.assertEqual(raw_movie['BoxOffice'], movie.BoxOffice)
        self.assertEqual(raw_movie['Director'], movie.Director)
        self.assertEqual(raw_movie['Title'], movie.Title)
        self.assertEqual(raw_movie['Year'], movie.Year)
        self.assertEqual(raw_movie['TomatoURL'], movie.TomatoURL)
        self.assertEqual(raw_movie['Actors'], movie.Actors)
        self.assertEqual(raw_movie['Genres'], movie.Genres)
        self.assertEqual(raw_movie['imdbRating'], movie.imdbRating)
        self.assertEqual(raw_movie['tomatoRating'], movie.tomatoRating)
        self.assertEqual(raw_movie['tomatoUserRating'], movie.tomatoUserRating)
        self.assertEqual(raw_movie['plot'], movie.plot)
        self.assertEqual(raw_movie['tomatoConsensus'], movie.tomatoConsensus)
        self.assertEqual(raw_movie['Poster'], movie.Poster)
        self.assertEqual(raw_movie['imdbID'], movie.imdbID)


    def test_fill_with_invalid_movie(self):
            movie_with_none_init = Movie().fillWithJsonObject(None)
            self.assertEqual(movie_with_none_init, None)


class TestTweetSentiment(TestCase):

    def test_polarity_scores(self):
        """
        Tests a sentiment containing the word but in the middle of the sentence (both upper and lower cases)
        1. lower case 'but'
        2. upper case 'BUT'
        3. Text without 'but'
        """
        t_a = TweetSentiment("I hate Michael Bay films, but this one rules love it best sublime superb")
        t_a2 = TweetSentiment("I hate Michael Bay films, BUT this one rules love it best sublime superb")
        t_a3 = TweetSentiment("I hate Michael Bay films")

        self.assertEqual(t_a.polarity_scores()['sentiment'], 0.9578)
        self.assertEqual(t_a2.polarity_scores()['sentiment'], 0.9578)
        self.assertAlmostEqual(t_a3.polarity_scores()['sentiment'], -0.5719)

    def test_capitalized(self):
        """
        Tests whether the capitalized functions is working - we test whether the entire tweet is capitalized
        whether there are a mix of capitalized words
        whether just some of the letters in a word are capitalized
        and whether everything is uncapitalized
        """
        self.assertEqual(TweetSentiment.capitalized(['WHAT', 'ARE', 'WE', 'DOING']), False)
        self.assertEqual(TweetSentiment.capitalized(["What", "ARE", "we", "DOING"]), True)
        self.assertEqual(TweetSentiment.capitalized(["What, THe, HECk"]), False)
        self.assertEqual(TweetSentiment.capitalized(["what", "are", "we", "doing"]), False)

    def test__contains_least(self):
        """
        Tests various aspects of the contains_least function -
        1. The simple inversion of a sentiment because least is in front of it
        2. Identifying a variation on "at the very least" which shouldn't invert the score
        3. Same check, but a different distance from the words "at" and "least"
        """
        t_a = TweetSentiment("The least good movie")
        t_a2 = TweetSentiment("at the very least, it's a good movie")
        t_a3 = TweetSentiment("at least its a good movie")

        self.assertEqual(t_a._contains_least(1.9, ['The', 'least', 'good', 'movie'], 2), -1.9)
        self.assertEqual(t_a2._contains_least(2.35, ['at', 'the', 'very', 'least', 'it\'s', 'good', 'movie'], 5), 2.35)
        self.assertEqual(t_a3._contains_least(1.9, ['at', 'least', 'it\'s', 'good', 'movie'], 3), 1.9)

    def test_negate(self):
        """
        Tests the negate function
        1. Simple negation word
        2. Doesn't contain a negation word
        3. Uses a misspelt word that is contained in the negation list
        4. checks the least negation word
        5. checks whether it was "at least" which should not negate the word
        """
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
        """
        This checks the exclamation_boost function
        1. The exclamation boost of text with no exclamation points
        2. With a single exclamation point
        3. With 2 exclamation points
        4. With > 3 exclamation points
        """
        test1 = "OMG I can't believe it"
        test2 = "OMG I can't believe it!"
        test3 = "OMG I can't believe it!!"
        test4 = "This movie rules!!!!!!"

        self.assertEqual(TweetSentiment._exclamation_boost(test1), 0)
        self.assertEqual(TweetSentiment._exclamation_boost(test2), 0.25)
        self.assertEqual(TweetSentiment._exclamation_boost(test3), 0.50)
        self.assertEqual(TweetSentiment._exclamation_boost(test4), 1.00)

    def test__question_boost(self):
        """
        This checks the question_boost function
        1. The question boost of text with no question points
        2. With 2 question marks
        3. With 3 question marks
        4. With >3 question marks
        """
        test1 = "Isn't this movie total crap"
        test2 = "Isn't this movie total crap??"
        test3 = "Isn't this movie total crap???"
        test4 = "Isn't this movie total crap????"

        self.assertEqual(TweetSentiment._question_boost(test1), 0)
        self.assertEqual(TweetSentiment._question_boost(test2), 0.20)
        self.assertAlmostEqual(TweetSentiment._question_boost(test3), 0.30)  # this was giving a digit in the millionth place
        self.assertEqual(TweetSentiment._question_boost(test4), 1.00)

    def test__organize_scores(self):
        """
        This tests the organize scores function, which puts negative, neutral and positive sentiments into various score values
        1. Fully positive set of scores
        2. Fully negative set of scores
        3. Mix of positive and negative scores
        4. Mix of positive, negative, and neutral scores
        """
        test1 = [2, 3, 2, 5]
        test2 = [-2, -3, -2, -5]
        test3 = [2, -3, 2, -5]
        test4 = [2, 0, -3, 0, 2, -5]

        self.assertEqual(list(TweetSentiment._organize_scores(test1)), [12.0, 0.0, 0])
        self.assertEqual(list(TweetSentiment._organize_scores(test2)), [0.0, -12.0, 0])
        self.assertEqual(list(TweetSentiment._organize_scores(test3)), [4.0, -8.0, 0])
        self.assertEqual(list(TweetSentiment._organize_scores(test4)), [4.0, -8.0, 2])

    def test_normalize(self):
        """
        Tests the normalize function
        1. a score above the reasonable positive range
        2. a score below the reasonable negative range
        3. a score right on the boundary of acceptable positive scores
        4. a score on the boundary of acceptable negative scores
        5. a score well within the bounds of a normal score
        6. a zero score
        """
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
        """
        Tests whether the words_and_symbols tokenizer is working correctly
        1. removes words with a single letter test
        2. retains misspelt words (for potential autocorrect in the future)
        3. Making sure it retains negative words
        4. Ensures it drops all numerical words
        5. Ensures it keeps the word 'never'
        """
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
