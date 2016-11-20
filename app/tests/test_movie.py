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
