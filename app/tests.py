## =============================================================================
## tests.py
## =============================================================================

from django.test import TestCase
from app.models import *
from datetime import datetime
import twitter
import omdb
import json

class TweetTest(TestCase):

    def setUp(self):
        Tweet.objects.create(
                text='Hello world',
                tweetID=1234567,
                created_at=datetime.now(),
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
        current_datetime=datetime.now()
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
                created_at=datetime.strftime(datetime.now(), '%a %b %d %H:%M:%S +0000 %Y'),
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
                'YomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genres' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatorUserRating' : 6.7,
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
        self.assertEqual(raw_movie['YomatoURL'], movie.YomatoURL)
        self.assertEqual(raw_movie['Actors'], movie.Actors)
        self.assertEqual(raw_movie['Genres'], movie.Genres)
        self.assertEqual(raw_movie['imdbRating'], movie.imdbRating)
        self.assertEqual(raw_movie['tomatoRating'], movie.tomatoRating)
        self.assertEqual(raw_movie['tomatorUserRating'], movie.tomatorUserRating)
        self.assertEqual(raw_movie['plot'], movie.plot)
        self.assertEqual(raw_movie['tomatoConsensus'], movie.tomatoConsensus)
        self.assertEqual(raw_movie['Poster'], movie.Poster)
        self.assertEqual(raw_movie['imdbID'], movie.imdbID)
