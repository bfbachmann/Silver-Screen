## =============================================================================
##  views.py
## =============================================================================
## - Manage web requests and responses

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from datetime import datetime
import json

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
            # redirect to a new URL:
            return render(request, 'results.html', {'form': query_form})

    ## If a GET we'll create a blank form
    elif request.method == "GET":
        query_form = QueryForm()
    ## Otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)

    return render(request, 'index.html', {'form': query_form})

## =============================================================================

## Handle User request for a certain movie and either progress to showing results
## from tweets or display informative error messages to the user
def results(request):
    """
    If the method is a POST processes the query the user submitted and returns the results
    Otherwise redirects to index
    """
    ## If its a post request we need to process it
    if request.method == 'POST':
        ## Extract the search term
        search_term = request.POST['query']
        movie = Movie()
        blank_form = QueryForm()
        data_to_render = {'error_message': None, 'form': blank_form}
        sum_scores = 0
        num_nonzero = 1

        ## Try get the movie from the database
        try:
            movie = Movie.objects.get(Title = search_term)

        ## If the movie is not in the db search OMDb
        except:
            try:
                movie = OMDbAPI().search(search_term)
            except ConnectionError:
                print('ERROR: Cannot connect to OMDb')
                data_to_render['error_message'] = 'Sorry, connection to the Open Movie Database failed. Please try again later.'
                return render(request, 'index.html', data_to_render)

        if not movie or not movie.Title:
            print('MOVIE: No matching movie')
            data_to_render['error_message'] = 'Sorry, we couldn\'t find a move with that title.'
            return render(request, 'index.html', data_to_render)

        ## Attempt to fetch tweets from the database
        clean_tweets = Tweet.objects.filter(imdbID = movie.imdbID)

        ## If we have too few tweets about a movie, search for more
        if not clean_tweets or len(clean_tweets) < 50:
            ## Get list of Statuses about the movie
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

            ## Create list of valid Tweet objects and calculate overall sentiment score
            clean_tweets = []
            positive_sum = 0
            positive_count = 0
            negative_sum = 0
            negative_count = 0
            if raw_tweets:
                for raw_tweet in raw_tweets:
                    new_tweet = Tweet().fillWithStatusObject(raw_tweet)
                    score = new_tweet.sentiment_score
                    clean_tweets.append(new_tweet)

                    ## Ensure that the sentiment score actually exists
                    if score and score != 0:
                        sum_scores += score
                        num_nonzero += 1

                        if score > 0:
                            positive_sum += score
                            positive_count += 1
                        elif score < 0:
                            negative_sum += score
                            negative_count += 1
            else:
                print('ERROR: No tweets found')
                data_to_render['error_message'] = 'Sorry, we couldn\'t find tweets about that movie.'
                return render(request, 'index.html', data_to_render)

        ## Chart sentiment scores of tweets
        negative_data, positive_data = create_chart_datasets(clean_tweets)

        data_to_render = {  'form': QueryForm(request.POST),
                            'tweets': clean_tweets[0:10],
                            'movie': movie,
                            'overall_score': round((sum_scores/num_nonzero + 1)*5, 1),
                            'polarity': int((positive_sum/positive_count - negative_sum/negative_count)/2*100),
                            'new_form': QueryForm(),
                            'negative_data': negative_data,
                            'positive_data': positive_data,
                        }
        return render(request, 'results.html', data_to_render)

    ## If request is GET redirect to index
    elif request.method == 'GET':
        return HttpResponseRedirect('/index/')
    ## Otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)

## =============================================================================

## Create a chart that displays the sentiment scores for the tweets associated with a movie
def create_chart_datasets(clean_tweets):
    negative_data = []
    positive_data = []

    for tweet in clean_tweets:
        score = tweet.sentiment_score
        data = {'y': abs(score)*100, 'x': str(datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S +0000 %Y')), 'r': 5}

        if score < 0:
            negative_data.append(data)
        else:
            positive_data.append(data)

    return negative_data, positive_data
