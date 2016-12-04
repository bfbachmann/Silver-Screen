from app.models.models import Tweet
from app.models.models import Movie
from django.test import TestCase
from django.utils import timezone
from datetime import datetime
import twitter

class TweetTest(TestCase):

    def setUp(self):
        Tweet.objects.create(
                text='Hello world',
                tweetID=1234567,
                created_at=timezone.make_aware(datetime.now()),
                favorite_count=9,
                lang='en',
                location='Russia',
                retweet_count=7,
                user_name='sara',
                user_screen_name='sarita',
                user_verified=True,
                sentiment_score=0.2647,
            )

        Movie.objects.create(
            Title= 'A great movie',
            Year= None,
            tomatoURL= None,
            Actors= None,
            BoxOffice= None,
            Genre= None,
            Director= None,
            imdbRating= None,
            tomatoRating= None,
            tomatoUserRating= None,
            Plot= None,
            tomatoConsensus= None,
            Poster= None,
            imdbID= '123456',
            recentVisits= 0,
            Awards= 'Golden Globe award',
            Country= 'Canada',
            Production= 'Lighthouse',
            Rated= 'PG-13',
            Released= 'December 12, 2014',
            Writer= 'Fancy Pants'
        )


    def test_fill_with_valid_status(self):
        current_datetime=timezone.make_aware(datetime.now())
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

        movie = Movie.objects.get(imdbID="123456")
        tweet=Tweet().fillWithStatusObject(sample_status, movie)

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
        self.assertEqual(tweet.linkedMovies.count(), 1)


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
                created_at=datetime.strftime(timezone.make_aware(datetime.now()), '%a %b %d %H:%M:%S +0000 %Y'),
                id=1234567,
                text='Hello world, again!',
                user=sample_user,
                retweet_count=1,
                favorite_count=5,
            )
        movie = Movie.objects.get(imdbID="123456")
        duplicate_tweet = Tweet().fillWithStatusObject(sample_status, movie)

        self.assertEqual(duplicate_tweet.text, 'Hello world')
