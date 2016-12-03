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
        search_term = request.GET['query'].replace('&amp;', '&')
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
            data_to_render['error_message'] = 'Sorry, we couldn\'t find a movie related to ' + search_term
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
        clean_tweets = [clean_tweet for clean_tweet in Tweet.objects.filter(linkedMovies__imdbID=movie.imdbID)]

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
                data_to_render['error_message'] = 'Sorry, we couldn\'t find tweets about ' + movie.Title
                return render(request, 'error.html', data_to_render)
            else:
                clean_tweets += get_clean_tweets(raw_tweets, movie)

        if ':' in movie.Title:
            messages.add_message(request, messages.INFO,
                                 "We couldn't find enough tweets about " + movie.Title + " so we're showing results for " + movie.Title.split(':')[0] + " instead.")

        ## If there aren't enough tweets to display tell the user
        if len(clean_tweets) < 5:
            data_to_render['error_message'] = 'Sorry, we couldn\'t find enough tweets about ' + movie.Title + ' movie for analysis.'
            return render(request, 'error.html', data_to_render)

        data_to_render = prepare_movie_data_for_render(request, clean_tweets, movie)
        return render(request, 'data.html', data_to_render)

    ## Otherwise return METHOD NOT ALLOWED
    else:
        return HttpResponse(status=403)

## =============================================================================

## Respond to request for about page
def overview(request):

    data_to_render = prepare_overview_data_for_render(request)

    return render(request, 'overview.html', data_to_render)


## =============================================================================

## Respond to request for overview page
def about(request):
    return render(request, 'about.html')

## =============================================================================

## Create a chart that displays the sentiment scores for the tweets associated with a movie
def create_chart_datasets(clean_tweets):
    negative_data = []
    positive_data = []
    neutral_count = 0

    for tweet in clean_tweets:
        score = tweet.sentiment_score

        if score != 0:
            data = {
                        'y': round(abs(score)*100,1),
                        'x': str(tweet.created_at),
                        'r': 5,
                        'tweet' : tweet.text
                    }

            if score < 0:
                negative_data.append(data)
            else:
                positive_data.append(data)
        else:
            neutral_count += 1

    return negative_data, positive_data, neutral_count

## =============================================================================

## Returns a list of Tweet objects created from the given list of twitter.Status objects
def get_clean_tweets(raw_tweets, movie):
    clean_tweets = []
    for raw_tweet in raw_tweets:
        clean_tweet = Tweet().fillWithStatusObject(raw_tweet, movie)
        if clean_tweet:
            clean_tweets.append(clean_tweet)
    return clean_tweets

## =============================================================================

## Returns a list of at most 10 Tweet objects whos sentiment scores are not 0
def get_tweets_to_display(clean_tweets):
    tweets_to_display = []
    i = 0
    while i < len(clean_tweets) and len(tweets_to_display) < 10:
        if clean_tweets[i].sentiment_score != 0:
            clean_tweets[i].sentiment_score = round((clean_tweets[i].sentiment_score+1)*5, 1)
            tweets_to_display.append(clean_tweets[i])
        i += 1

    return tweets_to_display

## =============================================================================

## Returns average sentiment score on a scale of 0 to 10, rounded to one decimal place
def get_overall_sentiment_score(clean_tweets):
    num_nonzero = 0
    sum_scores = 0

    for tweet in clean_tweets:
        score = tweet.sentiment_score
        if score != 0:
            num_nonzero += 1
            sum_scores += score

    if num_nonzero == 0:
        return 5.0
    return round((sum_scores/num_nonzero+1)*5, 1)

## =============================================================================

## Returns polarity of scentiment scores as a percentage #TODO THIS IS TERRIBLE
def get_polarity(clean_tweets):
    positive_count = 0
    negative_count = 0
    positive_sum = 0
    negative_sum = 0

    for tweet in clean_tweets:
        score = tweet.sentiment_score

        if score > 0:
            positive_count += 1
            positive_sum += score
        elif score < 0:
            negative_count += 1
            negative_sum += score

    if positive_count != 0 and negative_count != 0:
        return round((positive_sum/positive_count - negative_sum/negative_count)*50, 1)
    else:
        return 0

## =============================================================================

## Saves the given sentiment data to the db if it is not redundant
def save_new_sentiment(overall_score, movie):
    ## Find objects that are of the same movie and were made today
    duplicate = Sentiment.objects.filter(imdbID = movie.imdbID, sentimentDate = timezone.now())

    ## If there aren't duplicates create a new sentiment object for this movie
    if not duplicate:
        ## Populate the sentiment table with data for each movie with their scores at this time
        MovieSentiment = Sentiment(Title = movie.Title, imdbID = movie.imdbID, sentimentDate = timezone.now() , sentimentScore = overall_score)

        try:
            ## Movie doesn't exist yet (in the db) with this date so save it into the db
            MovieSentiment.save()
        except:
            print ("ERROR: couldn't save to sentiment table")
