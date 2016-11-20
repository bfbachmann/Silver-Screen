## =============================================================================
##  views.py
## =============================================================================
## - Manage web requests and responses

from django.shortcuts import render
from django.http import HttpResponse
from app.models.models import *
from app.models.helpers import *
from app.views.helpers import *
import datetime
from django.utils import timezone
from django.contrib import messages
from imdbpie import Imdb
from django.views.decorators.cache import never_cache
import random

## Initialize api objects
omdb = OMDbAPI()
twitter = TwitterAPI()

## =============================================================================

def index(request):
    """
    :param request: the HTTP request received from the client
    :return response: if the form is valid we show the user the results
                    otherwise we take the user back to 'index' and display the error
    """
    if request.method == 'POST':
        ## Create a form instance and populate it with data from the request:
        query_form = QueryForm(request.POST)

        ## Check whether it's valid:
        if query_form.is_valid():
            ## redirect to a new URL:
            return render(request, 'results.html', {'form': query_form})

    ## If a GET we'll create a blank form
    elif request.method == "GET":
        query_form = QueryForm()
    ## Otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)

    try:
        trendingMovie = Movie.objects.latest('recentVisits')
        if trendingMovie.recentVisits > 5:
            messages.add_message(request, messages.SUCCESS, trendingMovie.Title + ' is trending today!')
    except:
        pass

    return render(request, 'index.html', {'form': query_form})

## =============================================================================

## Takes the user to a loading page that waits for results from the server
def get_results_page(request):
    if request.method == 'POST':
        return render(request, 'results.html', {'query': request.POST['query']})

    return HttpResponse(status=403)

## =============================================================================

## Handle User request for a certain movie and either progress to showing results
## from tweets or display informative error messages to the user
@never_cache
def results(request):
    """
    If the method is a POST processes the query the user submitted and returns the results
    Otherwise redirects to index
    """
    ## If its a post request we need to process it
    if request.method == 'GET':
        ## Extract the search term
        search_term = request.GET['query']
        movie = Movie()
        blank_form = QueryForm()
        data_to_render = {'error_message': ''}
        sum_scores = 0
        num_nonzero = 1

        ## If no search term was given, pick a random one
        if not search_term or search_term == '':
            print('No search term given, picking random movie')
            imdb = Imdb()
            top250 = imdb.top_250()
            search_term = random.choice(top250).get('title')

        print('Search term: ' + search_term)

        ## Try get the movie from the database
        try:
            movie = Movie.objects.get(Title = search_term)

        ## If the movie is not in the db search OMDb
        except:
            print('Movie not found in database, searching OMDB')
            # try get the movie from OMDB
            try:
                movie = omdb.search(search_term)
            # if we couldn't get the movie from OMDB raise ConnectionError
            except ConnectionError:
                print('ERROR: Cannot connect to OMDb')
                data_to_render['error_message'] = 'Sorry, connection to the Open Movie Database failed. Please try again later.'
                return render(request, 'error.html', data_to_render)

        ## If no movie object was reaturned by OMDB or the database raise error
        if not movie or not movie.Title:
            print('ERROR: No matching movie')
            data_to_render['error_message'] = 'Sorry, we couldn\'t find a move with that title.'
            return render(request, 'error.html', data_to_render)
        else:
            movie.updateViews()

        ## Check if we have any sentiment data about this movie in our db
        try:
            mostRecentSentiment = Sentiment.objects.filter(imdbID = movie.imdbID).order_by('-sentimentDate')
        # if we don't have any sentiment about that movie just continue
        except:
            print("No sentiment found in database for this movie")

        ## Now we have a valid movie object, so try fetch tweets about this movie from the database
        clean_tweets = [clean_tweet for clean_tweet in Tweet.objects.filter(imdbID = movie.imdbID)]

        ## If we have too few tweets about the movie, or our sentiment is outdated, get more from Twitter
        if not clean_tweets or len(clean_tweets) < 50 or (mostRecentSentiment and mostRecentSentiment[0].sentimentDate < timezone.now() - datetime.timedelta(days=7)):
            print("Not enough tweets in our database or sentiment is out of date, searching Twitter for more")

            ## Get list of Statuses about the movie
            raw_tweets = []

            try:
                raw_tweets = twitter.search_movie(movie)
            except Exception as error:
                if type(error) is ValueError:
                    print('ERROR: Rate limit exceeded')
                    data_to_render['error_message'] = 'Sorry, SilverScreen\'s Twitter API rate limit has been exceeded. Please try a different movie, or try again later.'
                else:
                    print('ERROR: cannot connect to Twitter: ' + str(error))
                    data_to_render['error_message'] = 'Sorry, connection to Twitter failed. The Twitter API might be down. Please try again later.'
                return render(request, 'error.html', data_to_render)


            ## If we have no raw tweets to process raise error
            if not raw_tweets or len(raw_tweets) == 0:
                print('ERROR: No tweets found')
                data_to_render['error_message'] = 'Sorry, we couldn\'t find tweets about that movie.'
                return render(request, 'error.html', data_to_render)
            else:
                clean_tweets += get_clean_tweets(raw_tweets, movie.Title)

        ## If there aren't enough tweets to display tell the user
        if len(clean_tweets) < 5:
            data_to_render['error_message'] = 'Sorry, we couldn\'t find enough tweets about that movie for analysis.'
            return render(request, 'error.html', data_to_render)

        data_to_render = prepare_data_for_render(request, clean_tweets, movie)
        return render(request, 'data.html', data_to_render)

    ## Otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)

## =============================================================================

## Respond to request for about page
def about(request):
    return render(request, 'about.html')
