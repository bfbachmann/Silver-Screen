from django.test import TestCase
from app.models.models import *
from app.models.helpers import TwitterAPI
import twitter
import json

class TwitterAPITest(TestCase):

    def test_search_valid_movie(self):
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
                'Poster' : 'https://test.example.com/',
                'imdbID' : 284957
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertTrue(isinstance(response, list))

        for tweet in response:
            self.assertTrue(isinstance(tweet, twitter.models.Status))
            self.assertEqual(tweet.lang, 'en')
            self.assertEqual(tweet.imdbID, 284957)


    def test_search_movie_no_title(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$5,837,038',
                'Director': 'Mike Mikleton',
                'Title' : '',
                'Year' : 1998,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/back_to_the_future',
                'Actors' : 'Johnny Cage',
                'Genres' : 'Thriller',
                'imdbRating' : 7.9,
                'tomatoRating' : 8.2,
                'tomatoUserRating' : 5.8,
                'plot' : 'Two guys build a time machine and break it.',
                'tomatoConsensus' : 'Just a magnificent movie overall.',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 893792
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertEqual(response, None)

    def test_search_movie_invalid_title(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$93,837,038',
                'Director': 'Mike Mikleton',
                'Title' : 2907432,
                'Year' : 1998,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/back_to_the_future',
                'Actors' : 'Johnny Cage',
                'Genres' : 'Thriller',
                'imdbRating' : 7.9,
                'tomatoRating' : 8.2,
                'tomatoUserRating' : 5.8,
                'plot' : 'Two guys build a time machine and break it.',
                'tomatoConsensus' : 'Just a magnificent movie overall.',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 893792
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertEqual(response, None)

    def test_search_movie_complex_title1(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$36,983,927',
                'Director': 'David Blain',
                'Title' : 'Lord of The Rings: The Return of the King',
                'Year' : 2005,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genres' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatoUserRating' : 6.7,
                'plot' : 'Ben finds love and then his heart gets broken',
                'tomatoConsensus' : 'A coming of age tale of two people in love',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 284957
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertTrue(response != None)
        self.assertTrue(isinstance(response, list))

        for tweet in response:
            self.assertTrue(isinstance(tweet, twitter.models.Status))
            self.assertEqual(tweet.lang, 'en')
            self.assertEqual(tweet.imdbID, 284957)

    def test_search_movie_complex_title2(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$36,983,927',
                'Director': 'David Blain',
                'Title' : 'Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb',
                'Year' : 2005,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genres' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatoUserRating' : 6.7,
                'plot' : 'Ben finds love and then his heart gets broken',
                'tomatoConsensus' : 'A coming of age tale of two people in love',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 284957
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertTrue(response != None)
        self.assertTrue(isinstance(response, list))

        for tweet in response:
            self.assertTrue(isinstance(tweet, twitter.models.Status))
            self.assertEqual(tweet.lang, 'en')
            self.assertEqual(tweet.imdbID, 284957)

    def test_search_movie_simple_title(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$36,983,927',
                'Director': 'David Blain',
                'Title' : 'Up',
                'Year' : 2005,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genres' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatoUserRating' : 6.7,
                'plot' : 'Ben finds love and then his heart gets broken',
                'tomatoConsensus' : 'A coming of age tale of two people in love',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 284957
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertTrue(response != None)
        self.assertTrue(isinstance(response, list))

        for tweet in response:
            self.assertTrue(isinstance(tweet, twitter.models.Status))
            self.assertEqual(tweet.lang, 'en')
            self.assertEqual(tweet.imdbID, 284957)

    def test_search_movie_no_tweets(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$36,983,927',
                'Director': 'David Blain',
                'Title' : ')_(*&%#(UOJHOD*))',
                'Year' : 2005,
                'TomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genres' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatoUserRating' : 6.7,
                'plot' : 'Ben finds love and then his heart gets broken',
                'tomatoConsensus' : 'A coming of age tale of two people in love',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 284957
            }))

        valid_movie = Movie().fillWithJsonObject(raw_movie)
        response = TwitterAPI().search_movie(valid_movie)
        self.assertEqual(response, None)
