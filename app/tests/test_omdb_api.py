from django.test import TestCase
from app.models.models import Movie
from app.models.helpers import OMDbAPI
import omdb
import json

class OMDbAPITest(TestCase):

    def test_search_valid_movie(self):
        response = OMDbAPI().search('shutter island')

        self.assertTrue(isinstance(response, Movie))
        self.assertEqual(response.Title, 'Shutter Island')
        self.assertEqual(response.Director, 'Martin Scorsese')
        self.assertEqual(response.BoxOffice, '$125,001,000.00')
        self.assertEqual(response.tomatoConsensus, 'It may not rank with Scorsese\'s best work, but Shutter Island\'s gleefully unapologetic genre thrills represent the director at his most unrestrained.')
        self.assertEqual(response.Actors, 'Leonardo DiCaprio, Mark Ruffalo, Ben Kingsley, Max von Sydow')
        self.assertEqual(response.Year, '2010')
        self.assertTrue(response.imdbRating >= 0 and response.imdbRating <= 10)
        self.assertTrue(response.tomatoUserRating >= 0 and response.tomatoUserRating <= 10)
        self.assertTrue(response.tomatoRating >= 0 and response.tomatoRating <= 10)
        self.assertEqual(response.tomatoURL, 'http://www.rottentomatoes.com/m/1198124-shutter_island/')

    def test_search_movie_no_title(self):
        self.assertEqual(OMDbAPI().search(''), None)

    def test_search_movie_invalid_title(self):
        self.assertEqual(OMDbAPI().search(')(*&j3h)'), None)

    def test_search_movie_complex_title(self):
        response = OMDbAPI().search('The Good, the Bad and the Ugly')

        self.assertTrue(isinstance(response, Movie))
        self.assertEqual(response.Title, 'The Good, the Bad and the Ugly')
        self.assertEqual(response.Director, 'Sergio Leone')
        self.assertEqual(response.tomatoConsensus, 'Arguably the greatest of the spaghetti westerns, this epic features a compelling story, memorable performances, breathtaking landscapes, and a haunting score.')
        self.assertEqual(response.Actors, 'Eli Wallach, Clint Eastwood, Lee Van Cleef, Aldo Giuffrè')
        self.assertEqual(response.Year, '1966')
        self.assertTrue(response.imdbRating >= 0 and response.imdbRating <= 10)
        self.assertTrue(response.tomatoUserRating >= 0 and response.tomatoUserRating <= 10)
        self.assertTrue(response.tomatoRating >= 0 and response.tomatoRating <= 10)
        self.assertEqual(response.tomatoURL, 'http://www.rottentomatoes.com/m/the_good_the_bad_and_the_ugly/')

    def test_autocorrect_title(self):
        response = OMDbAPI().search('the bourne ultimatum')

        self.assertTrue(isinstance(response, Movie))
        self.assertEqual(response.Title, 'The Bourne Ultimatum')
        self.assertEqual(response.Director, 'Paul Greengrass')
        self.assertEqual(response.tomatoConsensus, 'The Bourne Ultimatum is an intelligent, finely tuned non-stop thrill ride. Another strong performance from Matt Damon and sharp camerawork from Paul Greengrass make this the finest installment of the Bourne trilogy.')
        self.assertEqual(response.Actors, 'Matt Damon, Julia Stiles, David Strathairn, Scott Glenn')
        self.assertEqual(response.Year, '2007')
        self.assertTrue(response.imdbRating >= 0 and response.imdbRating <= 10)
        self.assertTrue(response.tomatoUserRating >= 0 and response.tomatoUserRating <= 10)
        self.assertTrue(response.tomatoRating >= 0 and response.tomatoRating <= 10)
        self.assertEqual(response.tomatoURL, 'http://www.rottentomatoes.com/m/bourne_ultimatum/')
