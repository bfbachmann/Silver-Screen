from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from datetime import datetime
import json



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
        sum_scores = 0
        num_nonzero = 1

        # try get the movie from the database
        try:
            movie = Movie.objects.get(Title = search_term)

        # if the movie is not in the db search OMDB
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

        # attempt to fetch tweets from the database
        clean_tweets = Tweet.objects.filter(imdbID = movie.imdbID)

        # if we have no tweets about the movie
        if not clean_tweets:
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

            # create list of valid Tweet objects and calculate overall sentiment score
            clean_tweets = []
            if raw_tweets:
                for raw_tweet in raw_tweets:
                    new_tweet = Tweet().fillWithStatusObject(raw_tweet)
                    score = new_tweet.sentiment_score
                    clean_tweets.append(new_tweet)

                    if score and score != 0: #Ensure that the sentiment score actually exists
                        sum_scores += score
                        num_nonzero += 1
            else:
                print('ERROR: No tweets found')
                data_to_render['error_message'] = 'Sorry, we couldn\'t find tweets about that movie.'
                return render(request, 'index.html', data_to_render)

        negative_data, positive_data = create_chart_datasets(clean_tweets)
        data_to_render = {  'form': QueryForm(request.POST),
                            'tweets': clean_tweets,
                            'movie': movie,
                            'overall_score': sum_scores/num_nonzero,
                            'new_form': QueryForm(),
                            'negative_data': negative_data,
                            'positive_data': positive_data
                        }
        return render(request, 'results.html', data_to_render)

    # if request is GET redirect to index
    elif request.method == 'GET':
        return HttpResponseRedirect('/index/')
    # otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)


def create_chart_datasets(clean_tweets):
    negative_data = []
    positive_data = []

    for tweet in clean_tweets:
        score = tweet.sentiment_score
        data = {'y': score, 'x': str(datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S +0000 %Y')), 'r': abs(score)*10}

        if score < 0:
            negative_data.append(data)
        else:
            positive_data.append(data)

    return negative_data, positive_data
