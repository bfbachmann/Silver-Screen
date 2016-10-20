from django.db import models
from django import forms
import twitter
import yaml

class QueryForm(forms.Form):
    query = forms.CharField(label='Movie Title', max_length=100)


class TwitterAPIWrapper(object):

    def __init__(self):
        # load the API keys from api_keys.txt
        with open("scripts/twitter_api/api_keys.yml", 'r') as stream:
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
