from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *

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
        raw_tweets = search_twitter(request.POST['query'])
        clean_tweets = []
        for tweet in raw_tweets:
            clean_tweets.append(Tweet().fillWithStatusObject(tweet))
        omdbdata = search_omdb(request.POST['query'])
        return render(request, 'results.html', {'form': QueryForm(request.POST), 'tweets': clean_tweets, 'movie': omdbdata})
    else:
        return HttpResponseRedirect('/index/')


def search_twitter(search_term):
    wrapper = TwitterAPI()
    return wrapper.search(search_term)

def search_omdb(search_term):
    wrapper = OMDbAPI()
    return wrapper.search(search_term)
