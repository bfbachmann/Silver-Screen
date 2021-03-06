from django.test import TestCase
from app.models.models import Movie
import json

class MovieTest(TestCase):

    def test_fill_with_valid_movie(self):
        raw_movie = json.loads(json.dumps({
                'BoxOffice': '$36,983,927',
                'Director': 'David Blain',
                'Title' : 'The Amazing Race',
                'Year' : 2005,
                'tomatoURL' : 'http://https://www.rottentomatoes.com/m/arrival_2016',
                'Actors' : 'Johnny Deppp, Sara Connelly',
                'Genre' : 'Drama, Horror',
                'imdbRating' : 3.4,
                'tomatoRating' : 5.8,
                'tomatoUserRating' : 6.7,
                'Plot' : 'Ben finds love and then his heart gets broken',
                'tomatoConsensus' : 'A coming of age tale of two people in love',
                'Poster' : 'https://test.example.com/',
                'imdbID' : 284957,
                'Awards' : 'Golden Globe award',
                'Country' : 'Canada',
                'Production' : 'Lighthouse',
                'Rated' : 'PG-13',
                'Released' : 'December 12, 2014',
                'Writer' : 'Fancy Pants'
            }))

        movie = Movie().fillWithJsonObject(raw_movie)

        self.assertEqual(raw_movie['BoxOffice'], movie.BoxOffice)
        self.assertEqual(raw_movie['Director'], movie.Director)
        self.assertEqual(raw_movie['Title'], movie.Title)
        self.assertEqual(raw_movie['Year'], movie.Year)
        self.assertEqual(raw_movie['tomatoURL'], movie.tomatoURL)
        self.assertEqual(raw_movie['Actors'], movie.Actors)
        self.assertEqual(raw_movie['Genre'], movie.Genre)
        self.assertEqual(raw_movie['imdbRating'], movie.imdbRating)
        self.assertEqual(raw_movie['tomatoRating'], movie.tomatoRating)
        self.assertEqual(raw_movie['tomatoUserRating'], movie.tomatoUserRating)
        self.assertEqual(raw_movie['Plot'], movie.Plot)
        self.assertEqual(raw_movie['tomatoConsensus'], movie.tomatoConsensus)
        self.assertEqual(raw_movie['Poster'], movie.Poster)
        self.assertEqual(raw_movie['imdbID'], movie.imdbID)
        self.assertEqual(raw_movie['Awards'], movie.Awards)
        self.assertEqual(raw_movie['Country'], movie.Country)
        self.assertEqual(raw_movie['Production'], movie.Production)
        self.assertEqual(raw_movie['Rated'], movie.Rated)
        self.assertEqual(raw_movie['Released'], movie.Released)
        self.assertEqual(raw_movie['Writer'], movie.Writer)


    def test_fill_with_invalid_movie(self):
            movie_with_none_init = Movie().fillWithJsonObject(None)
            self.assertEqual(movie_with_none_init, None)
