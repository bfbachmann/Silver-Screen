import twitter
import yaml
import omdb
import os
import datetime
import concurrent.futures
from app.models.models import *

## =============================================================================
##  TwitterAPI
## =============================================================================

## API wrapper for Twitter
class TwitterAPI(object):

    ## Initialisation
    def __init__(self):
        ## Load the API keys
        try:
            stream = open("scripts/twitter_api/api_keys.yml", 'r')
            keys = yaml.load(stream)
        except:
            print('Failed to load Twitter API keys from file, falling back on environment variables')
            keys = {
                'consumer_key': os.environ['consumer_key'],
                'consumer_secret': os.environ['consumer_secret'],
                'access_token_key': os.environ['access_token_key'],
                'access_token_secret': os.environ['access_token_secret'],
            }

        self.tc = TitleCleaner()
        self.api = twitter.Api(consumer_key=keys['consumer_key'], consumer_secret=keys['consumer_secret'], access_token_key=keys['access_token_key'],  access_token_secret=keys['access_token_secret'], sleep_on_rate_limit=False) # NOTE: setting sleep_on_rate_limit to True here means the application will sleep when we hit the API rate limit. It will sleep until we can safely make another API call. Making this False will make the API throw a hard error when the rate limit is hit.

    ## Request tweets for a given movie
    def search_movie(self, movie):
        """
        :param movie: a Movie object with valid fields
        :return tweets: A List<twitter.models.Status> containing statuses posted between one year before the movie was
                        released and the current date if movie is a Movie object
                        Otherwise returns None
        """
        if not movie.Title or not isinstance(movie, Movie) or (not isinstance(movie.Title, str)):
            return None

        edited_title = self.tc.clean_title(movie.Title)
        imdbID = movie.imdbID
        current_datetime = timezone.now()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=7)
        futures = []
        tweets = []

        print('Searching Twitter for \"' + edited_title + '\"')

        for diff in range(0, 6):
            futures.append(executor.submit(self._make_request, edited_title, current_datetime, diff, imdbID))

        for future in futures:
            tweets += future.result()

        if tweets == []:
            return None
        return tweets


    def _make_request(self, edited_title, current_datetime, diff, imdbID):
        from_date = (current_datetime - datetime.timedelta(days=7-diff)).strftime('%Y-%m-%d')
        to_date = (current_datetime - datetime.timedelta(days=6-diff)).strftime('%Y-%m-%d')

        tweets = []

        ## Make search request
        ## Request not to recieve tweets that contain links, follow the RT pattern of retweets
        try:
            response = self.api.GetSearch(term='"'+edited_title +'" -filter:links -RT', since=from_date, until=to_date, lang='en', result_type='mixed')
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
##  OMDbAPI
## =============================================================================

## Handles movie titles that might produce bad Twitter search results
class TitleCleaner(object):

    def __init__(self):

        #Lists are sourced from:
        with open("sentimentanalysis/uncommon_wordlist.txt", 'r') as f:
            self.uncommon_wordlist = f.readlines()  #list containing top 2000-5000 words in english language
        self.uncommon_wordlist = [word.lower().replace('\n','') for word in self.uncommon_wordlist]

        with open("sentimentanalysis/common_wordlist.txt", 'r') as f:
            self.common_wordlist = f.readlines()    #list containing top 2000 words in english language
        self.common_wordlist = [word.lower().replace('\n','') for word in self.common_wordlist]

    def __searchLists(self, title):
        for word in self.common_wordlist:
            if (title == word):
                return 1
        for word in self.uncommon_wordlist:
            if (title == word):
                return 3
        return 5


    def __is_common(self, title):
        words_in_title = title.lower().split()

        for word in words_in_title:
            if not word in self.common_wordlist and not word in self.uncommon_wordlist:
                return False

        return True

    ## If the movie title is common it appends " movie" to the end of the title
    def clean_title(self, title):
        new_title = title
        if self.__is_common(title):
            new_title = new_title + ' movie'

        if ':' in new_title:
            return new_title.split(':')[0]

        return new_title
