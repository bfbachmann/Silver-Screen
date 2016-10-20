from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import QueryForm
import twitter
import pprint
import yaml

# Render the front page of the website with the query form
# TODO: upadte this once we have analysis working
def index(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        query_form = QueryForm(request.POST)

        # check whether it's valid:
        if query_form.is_valid():
            # redirect to a new URL:
            return render(request, 'results.html', {'form': query_form})

     # if a GET (or any other method) we'll create a blank form
    else:
        query_form = QueryForm()

    return render(request, 'index.html', {'form': query_form})


def results(request):
    if request.method == 'POST':
        tweets = search_twitter(request.POST['query'])
        return render(request, 'results.html', {'form': QueryForm(request.POST), 'tweets': tweets})
    else:
        return HttpResponseRedirect('/index/')


def search_twitter(search_term):
    # load the API keys from api_keys.txt
    with open("scripts/twitter_api/api_keys.yml", 'r') as stream:
        try:
            keys = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    api = twitter.Api(consumer_key=keys['consumer_key'], consumer_secret=keys['consumer_secret'], access_token_key=keys['access_token_key'],  access_token_secret=keys['access_token_secret'])

    # get tweets related to search term
    tweets = api.GetSearch(term=search_term) # List<twitter.models.Status>

    return tweets
