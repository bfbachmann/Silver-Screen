from django import forms
import twitter
import yaml
import os
import omdb
import datetime
from django.db import models
from sentimentanalysis.analyzer import SentimentScorer



class QueryForm(forms.Form):
    query = forms.CharField(label='Movie Title', max_length=100)


class TwitterAPI(object):

    def __init__(self):
        self.api = twitter.Api(consumer_key=os.environ['consumer_key'], consumer_secret=os.environ['consumer_secret'], access_token_key=os.environ['access_token_key'],  access_token_secret=os.environ['access_token_secret'], sleep_on_rate_limit=False) # NOTE: setting sleep_on_rate_limit to True here means the application will sleep when we hit the API rate limit. It will sleep until we can safely make another API call. Making this False will make the API throw a hard error when the rate limit is hit.


    def search_movie(self, movie):
        """
        :param movie: a Movie object with valid fields
        :return tweets: A List<twitter.models.Status> containing statuses posted between one year before the movie was
                        released and the current date if movie is a Movie object
                        Otherwise returns None
        """
        if type(movie) != Movie or (not isinstance(movie.Title, str) and not isinstance(movie.Title, unicode)):
            return None

        current_datetime = datetime.datetime.now()
        tweets = []

        for diff in range(0, 6):
            from_date = (current_datetime - datetime.timedelta(days=7-diff)).strftime('%Y-%m-%d')
            to_date = (current_datetime - datetime.timedelta(days=6-diff)).strftime('%Y-%m-%d')

            response = self.api.GetSearch(term='"'+movie.Title +'" -filter:links', since=from_date, until=to_date, lang='en', result_type='mixed')

            for tweet in response:
                # tag movie with imdbID
                tweet.imdbID = movie.imdbID

                # only append Tweets in English
                if tweet.lang == 'en' or tweet.user.lang == 'en':
                    tweets.append(tweet)

        return tweets


class Movie(models.Model):
    Title = models.CharField(max_length=128)
    Year = models.IntegerField(null=True, blank=True)
    YomatoURL = models.CharField(max_length=1024, null=True, blank=True)
    Actors = models.CharField(max_length=1024, null=True, blank=True)
    BoxOffice = models.CharField(max_length=1024, null=True, blank=True)
    Genres = models.CharField(max_length=1024, null=True, blank=True)
    Director = models.CharField(max_length=1024, null=True, blank=True)
    imdbRating = models.FloatField(null=True, blank=True)
    tomatoRating = models.CharField(max_length=32, null=True, blank=True)
    tomatorUserRating = models.CharField(max_length=32, null=True, blank=True)
    plot = models.CharField(max_length=2048, null=True, blank=True)
    tomatoConsensus = models.CharField(max_length=1024, null=True, blank=True)
    Poster = models.CharField(max_length=1024, null=True, blank=True)
    imdbID = models.CharField(max_length=1024)

    param_defaults = {
        'Title': None,
        'Year': None,
        'YomatoURL': None,
        'Actors': None,
        'BoxOffice': None,
        'Genres': None,
        'Director': None,
        'imdbRating': None,
        'tomatoRating': None,
        'tomatoUserRating': None,
        'Plot': None,
        'tomatoConsensus': None,
        'Poster': None,
        'imdbID': None
    }

    def __unicode__(self):
        return self.Title

    def fillWithJsonObject(self, jsonObject):
        """
        :param jsonObject: a JSON Object containing information about a movie returned by the OMDbAPI
        :return self: this movie, udpated with the relevant data from the given jsonObject
        """
        if jsonObject is not None:
            for (key, value) in jsonObject.items():
                if key in self.param_defaults.keys():
                    if key == 'imdbRating' and not isinstance(value, float):
                        try:
                            value = float(value)
                        except:
                            value = None # TODO: we'll have to handle this upstream
                    setattr(self, key, value)
            self.save()
        return self



class OMDbAPI(object):

    def __init__(self):
        self.recentSearches = {}


    def search(self, title, year=None):
        """
        :params title: a string holding the title of the movie
        :return movie: if at least one movie with a similar title is found, this is a Movie object
                      created from the most relevant result returned by OMDb, otherwise it is empty list
        """

        # search for all movies with similar titles
        try:
            matching_movies = omdb.search_movie(title)
        except:
            raise ConnectionError

        self.recentSearches.update({title:matching_movies})

        #For now, only return most popular movie
        highestIMDB = 0

        if matching_movies:
            movie = matching_movies.pop(0)
            print("MOVIE: " + movie.title)

            try:
                movieObj = Movie.objects.get(imdbID=movie.imdb_id)
            except Movie.DoesNotExist:
                movieObj = None

            if not movieObj:
                response = omdb.request(i=movie.imdb_id, tomatoes=True, type='movie').json()
                movieObj = Movie().fillWithJsonObject(response)

            return movieObj
        else:
            return None

class Tweet(models.Model):
    text = models.CharField(max_length=256)
    tweetID = models.BigIntegerField(unique=True)
    created_at = models.CharField(max_length=256)
    favorite_count = models.IntegerField()
    lang = models.CharField(max_length=16)
    location = models.CharField(max_length=256)
    retweet_count = models.IntegerField()
    user_name = models.CharField(max_length=256)
    user_screen_name = models.CharField(max_length=256)
    user_verified = models.BooleanField()
    imdbID =  models.CharField(max_length=1024)
    sentiment_score = models.FloatField(null=True, blank=True)

    param_defaults = {
        'text' : None,
        'created_at' : None,
        'favorite_count' : None,
        'lang' : None,
        'location' : None,
        'retweet_count' : None,
        'user_name' : None,
        'user_screen_name' : None,
        'user_verified' : False,
        'sentiment_score' : False,
        'imdbID': False,
        'tweetID': False,
    }

    def fillWithStatusObject(self, tweet):
        """
        :param tweet: an object of the class twitter.Status (returnd by Twitter API)
        :return updated_tweet: this tweet, updated with the data from the given tweet
        """
        if tweet is None or type(tweet) is not twitter.Status:
            return self

        # assume the Tweet is in the users location if we have no info
        if type(tweet.location) is not str:
            tweet.location = tweet.user.location
        # assume the Tweet is in the users langauge if we have no info
        if tweet.lang is None and tweet.user.lang is not None:
            tweet.lang = tweet.user.lang

        self.text=tweet.text
        self.created_at=tweet.created_at
        self.favorite_count=tweet.favorite_count
        self.lang=tweet.lang
        self.location=tweet.location
        self.retweet_count=tweet.retweet_count
        self.user_name=tweet.user.name
        self.user_screen_name=tweet.user.screen_name
        self.user_verified=tweet.user.verified
        self.tweetID = tweet.id
        self.imdbID = tweet.imdbID
        self.sentiment_score = SentimentScorer("sentimentanalysis/lexicon_done.txt").polarity_scores(self.text)['sentiment']

        # only save this tweet if it isn't already in the database
        if Tweet.objects.filter(tweetID=self.tweetID) is None:
            try:
                self.save()
            except:
                print("Failed to save invalid tweet: " + str(self.tweetID))
                pass
        else:
            print("Failed to save duplicate tweet: " + str(self.tweetID))

        return self

    def __unicode__(self):
        return str(self.tweetID)
