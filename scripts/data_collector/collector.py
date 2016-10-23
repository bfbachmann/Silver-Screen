import omdb
import yaml
import twitter

class TwitterAPI(object):

    def __init__(self):
        # load the API keys from api_keys.txt
        with open("../twitter_api/api_keys.yml", 'r') as stream:
            try:
                keys = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.api = twitter.Api(consumer_key=keys['consumer_key'], consumer_secret=keys['consumer_secret'], access_token_key=keys['access_token_key'],  access_token_secret=keys['access_token_secret'], sleep_on_rate_limit=True) # NOTE: setting sleep_on_rate_limit to True here means the application will sleep when we hit the API rate limit. It will sleep until we can safely make another API call. Making this False will make the API throw a hard error when the rate limit is hit.


    # Searches Twitter for search_term and returns List<twitter.models.Status>
    # See https://github.com/bear/python-twitter/blob/master/twitter/api.py for docs on arguments
    def search(self, search_term, since=None, until=None, geocode=None):
        tweets = self.api.GetSearch(term=search_term, since=since, until=until, geocode=geocode)
        return tweets



class Movie(object):

    def __init__(self,**kwargs):
        self.param_defaults = {
             'Title':None,
             'Year':None,
             'YomatoURL':None,
             'Actors':None,
             'BoxOffice':None,
             'Genres':None,
             'Director':None,
             'imdbRating':None,
             'tomatoRating':None,
             'tomatoUserRating':None,
             'plot':None,
             'tomatoConsensus':None,
             'Poster':None
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))


    def fillWithJsonObject(self, jsonObject):
        for (key, value) in jsonObject.items():
            if key in self.param_defaults.keys():
                print('setting attribute: ' + key + ' with ' + value)
                setattr(self, key, value)
        return self



class OMDbAPI(object):

    def __init__(self):
        self.recentSearches = {}

    # @params:
    #       title: a string holding the title of the movie
    # @returns:
    #       movie: if at least one movie with a similar title is found, this is a Movie object
    #              created from the most relevant result returned by OMDb, otherwise it is None
    def search(self, title, year=None):
        # search for all movies with similar titles
        matching_movies = omdb.search_movie(title)
        self.recentSearches.update({title:matching_movies})

        #For now, only return most popular movie

        highestIMDB = 0

        if matching_movies:
            movie = matching_movies.pop(0)

            response = omdb.request(i=movie.imdb_id, tomatoes=True, type='movie').json()
            movieObj = Movie().fillWithJsonObject(response)

            return movieObj
        else:
            return None




omdb_api = OMDbAPI()
twitter_api = TwitterAPI()

output_file_yaml = open("tweets.yml", 'w')

with open('popular_movies.txt') as titles:
    for i, line in enumerate(titles):
        movie = omdb_api.search(line)
        if movie is not None:
            tweets = twitter_api.search(movie.Title)
            for tweet in tweets:
                yaml.dump(tweet, output_file_yaml, allow_unicode=True)
