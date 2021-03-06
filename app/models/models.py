## =============================================================================
##  models.py
## =============================================================================
## - Manage data

import datetime
import twitter
from django import forms
from django.db import models
from django.utils import timezone
from sentimentanalysis.analyzer import TweetSentiment
import html

## =============================================================================
##  QueryForm
## =============================================================================

class QueryForm(forms.Form):
    query = forms.CharField(label='Movie Title', max_length=100, required=False)

## =============================================================================
##  Movie
## =============================================================================

class Movie(models.Model):
    Title = models.CharField(max_length=128)
    Year = models.IntegerField(null=True, blank=True)
    tomatoURL = models.CharField(max_length=1024, null=True, blank=True)
    Actors = models.CharField(max_length=1024, null=True, blank=True)
    BoxOffice = models.CharField(max_length=1024, null=True, blank=True)
    Genre = models.CharField(max_length=1024, null=True, blank=True)
    Director = models.CharField(max_length=1024, null=True, blank=True)
    imdbRating = models.FloatField(null=True, blank=True)
    tomatoRating = models.FloatField(null=True, blank=True)
    tomatoUserRating = models.FloatField(null=True, blank=True)
    Plot = models.CharField(max_length=2048, null=True, blank=True)
    tomatoConsensus = models.CharField(max_length=1024, null=True, blank=True)
    Poster = models.CharField(max_length=1024, null=True, blank=True)
    imdbID = models.CharField(max_length=1024, unique=True, null=False, blank=False)
    recentVisits = models.IntegerField(default=0)
    Writer = models.CharField(max_length=1024, null=True, blank=True)
    Rated = models.CharField(max_length=1024, null=True, blank=True)
    Awards = models.CharField(max_length=2048, null=True, blank=True)
    Country = models.CharField(max_length=1024, null=True, blank=True)
    Production = models.CharField(max_length=1024, null=True, blank=True)
    Released = models.CharField(max_length=1024, null=True, blank=True)

    param_defaults = {
        'Title': None,
        'Year': None,
        'tomatoURL': None,
        'Actors': None,
        'BoxOffice': None,
        'Genre': None,
        'Director': None,
        'imdbRating': None,
        'tomatoRating': None,
        'tomatoUserRating': None,
        'Plot': None,
        'tomatoConsensus': None,
        'Poster': None,
        'imdbID': None,
        'recentVisits': None,
        'Writer': None,
        'Rated': None,
        'Awards': None,
        'Country': None,
        'Production': None,
        'Released': None,
    }

    def __unicode__(self):
        return self.Title

    ## Populate the current movie object parameters with the values recieved from
    ## a request to the OMDbAPI
    def fillWithJsonObject(self, jsonObject):
        """
        :param jsonObject: a JSON Object containing information about a movie returned by the OMDbAPI
        :return self:   this movie, udpated with the relevant data from the given jsonObject if it is valid
                        otherwise returns None
        """
        ## Just return the movie we have in the db if it is already there
        if jsonObject:
            try:
                movie_in_db = Movie.objects.get(imdbID=jsonObject['imdbID'])
            except Exception as exc:
                if isinstance(exc, KeyError):
                    return None
                movie_in_db = None

            if movie_in_db:
                print('OMDbAPI found movie in DB')
                return movie_in_db

            for (key, value) in jsonObject.items():
                if key in self.param_defaults.keys():
                    if 'Rating' in key:
                        try:
                            value = float(value)
                        except:
                            value = None

                    if isinstance(value, str):
                        if value == "N/A":
                            value = None
                        else:
                            value = value.strip()
                    setattr(self, key, value)

            try:
                self.save()
            except Exception as exc:
                print(str(exc))
                return None

            return self
        else:
            return None

    def updateViews(self):
        self.recentVisits += 1
        self.save()

## =============================================================================
##  Tweet
## =============================================================================

class Tweet(models.Model):
    ## Attributes of a tweet after dropping extraneous fields
    text = models.CharField(max_length=256)
    tweetID = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(default=None, null=True)
    favorite_count = models.IntegerField()
    lang = models.CharField(max_length=16)
    location = models.CharField(max_length=256)
    retweet_count = models.IntegerField()
    user_name = models.CharField(max_length=256)
    user_screen_name = models.CharField(max_length=256)
    user_verified = models.BooleanField()
    linkedMovies = models.ManyToManyField(Movie)
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
        'linkedMovies' : False,
        'tweetID': False,
    }

    ## Populate the current twitter object with values returned from a Twitter API request
    def fillWithStatusObject(self, tweet, movie):
        """
        :param tweet: an object of the class twitter.Status (returnd by Twitter API)
        :return updated_tweet: this tweet, updated with the data from the given tweet
        """
        ## Do not create a new Tweet object for this tweet if it is invalid
        if tweet is None or movie is None or not isinstance(tweet, twitter.Status):
            return None
        try:
            existingTweet = Tweet.objects.get(tweetID=tweet.id)

            ## If a Tweet object for this tweet exists, append its linkedMovies list

            existingTweet.linkedMovies.add(movie)
            existingTweet.save()
            return existingTweet
        except:
            pass

        ## Assume the Tweet is in the users location if we have no info
        if not isinstance(tweet.location, str):
            tweet.location = tweet.user.location

        ## Assume the Tweet is in the users langauge if we have no info
        if tweet.lang is None and tweet.user is not None and tweet.user.lang is not None:
            tweet.lang = tweet.user.lang

        ## Values from API request
        self.text=html.unescape(tweet.text)
        self.created_at=timezone.make_aware(datetime.datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S +0000 %Y'))
        self.favorite_count=tweet.favorite_count
        self.lang=tweet.lang
        self.location=tweet.location
        self.retweet_count=tweet.retweet_count
        self.user_name=tweet.user.name
        self.user_screen_name=tweet.user.screen_name
        self.user_verified=tweet.user.verified
        self.tweetID=tweet.id

        ## Remove words in movie title from tweet body so they don't influence sentiment score
        filtered_text = self.text.lower().split()
        for word in movie.Title.lower().split():
            if word in filtered_text:
                filtered_text.remove(word)

        filtered_text = " ".join(filtered_text)

        ## Assign sentiment score to the tweet
        self.sentiment_score = TweetSentiment(filtered_text).polarity_scores()['sentiment']

        ## Try save the tweet to the database
        try:
            self.save()
            self.linkedMovies.add(movie)
            self.save()
        except:
            pass

        return self

    def __unicode__(self):
        return str(self.tweetID)

## =============================================================================
##  Sentiment
## =============================================================================

class Sentiment(models.Model):
   Title = models.CharField(max_length=128)
   imdbID = models.CharField(max_length=1024)
   sentimentDate = models.DateTimeField(default=None, null=True)
   sentimentScore = models.FloatField(null=True, blank=True)
   polarity_score = models.FloatField(null=True, blank=True)

   param_defaults = {
       'Title': None,
       'imdbID': None,
       'sentimentDate': None,
       'sentimentScore': None,
       'positivityScore': None,
       'negativityScore': None,
       'neutralityScore': None
   }

   def __unicode__(self):
       return self.Title + self.imdbID

   def fillWithJsonObject(self, jsonObject):
       #:param jsonObject: a JSON Object containing information about a movie returned by the OMDbAPI
       #:return self: this movie, udpated with the relevant data from the given jsonObject
       if jsonObject is not None:
           for (key, value) in jsonObject.items():
               if key in self.param_defaults.keys():
                   setattr(self, key, value)
           self.save()
       return self
