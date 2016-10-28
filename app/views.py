from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *


# TODO: upadte this once we have analysis working
def index(request):
    """
    :param request: the HTTP request recieved from the client
    :return response: if the form is valid we show the user the results
                    otherwise we take the user back to 'index' and display the error
    """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        query_form = QueryForm(request.POST)

        # check whether it's valid:
        if query_form.is_valid():
            # redirect to a new URL:
            return render(request, 'results.html', {'form': query_form})

    # if a GET we'll create a blank form
    elif request.method == "GET":
        query_form = QueryForm()
    # otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)

    return render(request, 'index.html', {'form': query_form})



def results(request):
    """
    If the method is a POST processes the query the user submitted and returns the results
    Otherwise redirects to index
    """
    # if its a post request we need to process it
    if request.method == 'POST':
        # extract the search term
        search_term = request.POST['query']
        # search OMDB for the movie
        movie = OMDbAPI().search(search_term)
        # get list of Tweets about the movie
        raw_tweets = TwitterAPI().search_movie(movie)

        # create list of valid Tweet objects
        clean_tweets = []

        if raw_tweets:
            for raw_tweet in raw_tweets:
                clean_tweets.append(Tweet().fillWithJsonObject(raw_tweet))
        else:
            return render(request, 'index.html', {'error_message': 'Movie not found.', 'form': QueryForm()})

        data_to_render = {'form': QueryForm(request.POST), 'tweets': clean_tweets, 'movie': movie}
        return render(request, 'results.html', data_to_render)

    # if request is GET redirect to index
    elif request.method == 'GET':
        return HttpResponseRedirect('/index/')
    # otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)
