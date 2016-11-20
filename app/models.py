## =============================================================================
##  models.py
## =============================================================================
## - Manage data

from django import forms
import twitter
import yaml
import omdb
import datetime
from django.db import models
from django.utils import timezone
from sentimentanalysis.analyzer import TweetSentiment
import concurrent.futures

## =============================================================================
##  QueryForm
## =============================================================================

class QueryForm(forms.Form):
    query = forms.CharField(label='Movie Title', max_length=100, required=False)

## =============================================================================
##  TwitterAPI
## =============================================================================

## API wrapper for Twitter
class TwitterAPI(object):

    ## Initialisation
    def __init__(self):
        ## Load the API keys from api_keys.yml
        with open("scripts/twitter_api/api_keys.yml", 'r') as stream:
            try:
                keys = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.api = twitter.Api(consumer_key=keys['consumer_key'], consumer_secret=keys['consumer_secret'], access_token_key=keys['access_token_key'],  access_token_secret=keys['access_token_secret'], sleep_on_rate_limit=False) # NOTE: setting sleep_on_rate_limit to True here means the application will sleep when we hit the API rate limit. It will sleep until we can safely make another API call. Making this False will make the API throw a hard error when the rate limit is hit.

    ## Request tweets for a given movie
    def search_movie(self, movie):
        """
        :param movie: a Movie object with valid fields
        :return tweets: A List<twitter.models.Status> containing statuses posted between one year before the movie was
                        released and the current date if movie is a Movie object
                        Otherwise returns None
        """
        if not isinstance(movie.Title, str) and not isinstance(movie.Title, unicode):
            return None

        current_datetime = timezone.now()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=7)
        futures = []
        tweets = []

        for diff in range(0, 6):
            futures.append(executor.submit(self._make_request, movie.Title, movie.imdbID, current_datetime, diff))

        for future in futures:
            tweets += future.result()

        return tweets


    def _make_request(self, title, imdbID, current_datetime, diff):
        from_date = (current_datetime - datetime.timedelta(days=7-diff)).strftime('%Y-%m-%d')
        to_date = (current_datetime - datetime.timedelta(days=6-diff)).strftime('%Y-%m-%d')

        tweets = []

        ## Make search request
        ## Request not to recieve tweets that contain links, follow the RT pattern of retweets
        try:
            response = self.api.GetSearch(term='"'+title +'" -filter:links -RT', since=from_date, until=to_date, lang='en', result_type='mixed')
        except Exception as e:
            print(e)

        for tweet in response:
            ## Tag movie with imdbID
            tweet.imdbID = imdbID

            ## Only append Tweets in English
            if tweet.lang == 'en' or tweet.user.lang == 'en':
                tweets.append(tweet)

        return tweets

## =============================================================================
##  Movie
## =============================================================================

class Movie(models.Model):
    Title = models.CharField(max_length=128)
    SimplifiedTitle = models.CharField(max_length=128, blank=True)
    Year = models.IntegerField(null=True, blank=True)
    TomatoURL = models.CharField(max_length=1024, null=True, blank=True)
    Actors = models.CharField(max_length=1024, null=True, blank=True)
    BoxOffice = models.CharField(max_length=1024, null=True, blank=True)
    Genres = models.CharField(max_length=1024, null=True, blank=True)
    Director = models.CharField(max_length=1024, null=True, blank=True)
    imdbRating = models.FloatField(null=True, blank=True)
    tomatoRating = models.CharField(max_length=32, null=True, blank=True)
    tomatoUserRating = models.CharField(max_length=32, null=True, blank=True)
    plot = models.CharField(max_length=2048, null=True, blank=True)
    tomatoConsensus = models.CharField(max_length=1024, null=True, blank=True)
    Poster = models.CharField(max_length=1024, null=True, blank=True)
    imdbID = models.CharField(max_length=1024)
    recentVisits = models.IntegerField(default=0)
    useSimplified = models.BooleanField(default=False)

    param_defaults = {
        'Title': None,
        'SimplifiedTitle': None,
        'Year': None,
        'TomatoURL': None,
        'Actors': None,
        'BoxOffice': None,
        'Genres': None,
        'Director': None,
        'imdbRating': None,
        'tomatoRating': None,
        'tomatoUserRating': None,
        'plot': None,
        'tomatoConsensus': None,
        'Poster': None,
        'imdbID': None,
        'recentVisits': None,
        'useSimplified': None
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
        if jsonObject is not None:
            for (key, value) in jsonObject.items():
                if key in self.param_defaults.keys():
                    if key == 'imdbRating' and not isinstance(value, float):
                        try:
                            value = float(value)
                        except:
                            value = None # TODO: we'll have to handle this upstream

                    if isinstance(value, str):
                        if value == "N/A":
                            value = None
                        else:
                            value = value.strip()
                    setattr(self, key, value)

            if self.Title and ":" in self.Title:
                self.SimplifiedTitle = self.Title.rpartition(':')[0]

            if self.Title and "-" in self.Title:
                splitStr = self.Title.rpartition('-')[0]
                if len(splitStr) > len(self.SimplifiedTitle):
                    self.SimplifiedTitle = splitStr

            self.save()
            return self
        else:
            return None


    def updateViews(self):
        self.recentVisits = self.recentVisits+1
        self.save()

    def updateTitleStatus(self,useSimplified):
        self.useSimplified = useSimplified
        self.save()

## =============================================================================
##  OMDbAPI
## =============================================================================

## API wrapper for OMDb
class OMDbAPI(object):

    def __init__(self):
        pass

    ## Search the OMDb database for movies with titles that match the requested movie
    def search(self, title):
        """
        :params title: a string holding the title of the movie
        :return movie: if at least one movie with a similar title is found, this is a Movie object
                      created from the most relevant result returned by OMDb, otherwise it is empty list
        """
        ## Search for all movies with similar titles
        try:
            matching_movies = omdb.search_movie(title)
        except:
            raise ConnectionError

        ## For now, only return most popular movie
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
                if not movieObj:
                    return None

            return movieObj
        else:
            return None


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

    ## Populate the current twitter object with values returned from a Twitter API request
    def fillWithStatusObject(self, tweet, movie_title):
        """
        :param tweet: an object of the class twitter.Status (returnd by Twitter API)
        :return updated_tweet: this tweet, updated with the data from the given tweet
        """
        ## Do not create a new Tweet object for this tweet if it is invalid or already exists in our db
        if tweet is None or not isinstance(tweet, twitter.Status) or Tweet.objects.filter(tweetID=tweet.id):
            return None

        ## Assume the Tweet is in the users location if we have no info
        if not isinstance(tweet.location, str):
            tweet.location = tweet.user.location

        ## Assume the Tweet is in the users langauge if we have no info
        if tweet.lang is None and tweet.user is not None and tweet.user.lang is not None:
            tweet.lang = tweet.user.lang

        ## Values from API request
        self.text=tweet.text
        self.created_at=datetime.datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S +0000 %Y')
        self.favorite_count=tweet.favorite_count
        self.lang=tweet.lang
        self.location=tweet.location
        self.retweet_count=tweet.retweet_count
        self.user_name=tweet.user.name
        self.user_screen_name=tweet.user.screen_name
        self.user_verified=tweet.user.verified
        self.tweetID=tweet.id
        self.imdbID=tweet.imdbID

        ## Remove words in movie title from tweet body so they don't influence sentiment score
        filtered_text = self.text.lower().split()
        for word in movie_title.lower().split():
            if word in filtered_text:
                filtered_text.remove(word)

        filtered_text = " ".join(filtered_text)

        ## Assign sentiment score to the tweet
        self.sentiment_score = TweetSentiment(filtered_text).polarity_scores()['sentiment']

        ## Try save the tweet to the database
        try:
            self.save()
        except:
            print("Failed to save invalid tweet: " + str(self.tweetID))

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
