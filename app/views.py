from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *


# TODO: upadte this once we have analysis working
def index(request):
    """
    :param request: the HTTP request received from the client
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
        movie = Movie()
        blank_form = QueryForm()
        data_to_render = {'error_message': None, 'form': blank_form}

        try:
            movie = OMDbAPI().search(search_term)
        except ConnectionError:
            print('ERROR: Cannot connect to OMDb')
            data_to_render['error_message'] = 'Sorry, connection to the Open Movie Database failed. Please try again later.'
            return render(request, 'index.html', data_to_render)

        if not movie or not movie.Title:
            print('ERROR: No matching movie')
            data_to_render['error_message'] = 'Sorry, we couldn\'t find a move with that title.'
            return render(request, 'index.html', data_to_render)

        # get list of Statuses about the movie
        raw_tweets = []
        try:
            raw_tweets = TwitterAPI().search_movie(movie)
        except Exception as error:
            if type(error) is ValueError:
                print('ERROR: Rate limit exceeded')
                data_to_render['error_message'] = 'Sorry, SilverScreen\'s Twitter API rate limit has been exceeded. Please try a different movie, or try again later.'
            else:
                print('ERROR: cannot connect to Twitter')
                data_to_render['error_message'] = 'Sorry, connection to Twitter failed. The Twitter API might be down. Please try again later.'
            return render(request, 'index.html', data_to_render)

        # create list of valid Tweet objects
        clean_tweets = []
        if raw_tweets:
            for raw_tweet in raw_tweets:
                clean_tweets.append(Tweet().fillWithStatusObject(raw_tweet))
        else:
            print('ERROR: No tweets found')
            data_to_render['error_message'] = 'Sorry, we could\'nt find tweets about that movie.'
            return render(request, 'index.html', data_to_render)

        data_to_render = {'form': QueryForm(request.POST), 'tweets': clean_tweets, 'movie': movie}
        return render(request, 'results.html', data_to_render)

    # if request is GET redirect to index
    elif request.method == 'GET':
        return HttpResponseRedirect('/index/')
    # otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)
