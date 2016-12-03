from app.models.models import *
from django.shortcuts import render
import datetime
import difflib


## A singleton class for caching successful responses
class ResponseCache:
    class __ResponseCache:
        def __init__(self, most_recent_response):
            self.most_recent_response = most_recent_response

    instance = None

    def __init__(self, most_recent_response):
        if not ResponseCache.instance:
            ResponseCache.instance = ResponseCache.__ResponseCache(most_recent_response)
        else:
            print('CACHING RESPONSE: ' + most_recent_response['movie'].Title)
            ResponseCache.instance.most_recent_response = most_recent_response

    def get_most_recent(self):
        return ResponseCache.instance.most_recent_response

cache = ResponseCache(None)

## =============================================================================

## Handles sending an error message to the user when their request has failed
def error_response(request, message):
    previous_result = cache.get_most_recent()

    if not previous_result:
        print('RETURNING ONLY ERROR RESPONSE')
        return render(request, 'error.html', {'error_message' : message})

    previous_result['error_message'] = message
    print('RETURNING ERROR RESPONSE WITH CACHED CONTENT')
    return render(request, 'data.html', previous_result)

## =============================================================================

## Autocorrect poorly formed search terms based on current titles in db
def autocorrect_search_term(search_term):
    search_term = search_term.replace('&amp;', '&').title()
    movie_titles = Movie.objects.all().values_list('Title')
    matches = difflib.get_close_matches(search_term, movie_titles, n=1)
    if len(matches) == 0:
        return search_term
    return matches[0]

## =============================================================================

## Processes clean_tweets and returns dictionary of data to render
def prepare_data_for_render(request, clean_tweets, movie):
    ## Chart sentiment scores of tweets
    overall_score = get_overall_sentiment_score(clean_tweets)
    polarity = get_polarity(clean_tweets)
    negative_data, positive_data, neutral_count = create_chart_datasets(clean_tweets)
    positive_avgs, negative_avgs = get_daily_avgs(clean_tweets)
    tweets_to_display = get_tweets_to_display(clean_tweets)

    ## Save our new sentiment data to the db
    save_new_sentiment(overall_score, movie)

    ## Prepare data to render on results page
    data_to_render = {  'form'          : QueryForm(request.POST),
                        'tweets'        : tweets_to_display,
                        'movie'         : movie,
                        'overall_score' : overall_score,
                        'polarity'      : polarity,
                        'new_form'      : QueryForm(),
                        #  Begin chart data
                        'negative_data' : negative_data,
                        'positive_data' : positive_data,
                        'negative_count': len(negative_data),
                        'positive_count': len(positive_data),
                        'neutral_count' : neutral_count,
                        'positive_avgs' : positive_avgs,
                        'negative_avgs' : negative_avgs,
                    }
    cache = ResponseCache(data_to_render)
    return data_to_render

## =============================================================================

## Create datasets for chart that displays the sentiment scores for each tweet
def create_chart_datasets(clean_tweets):
    negative_data = []
    positive_data = []
    neutral_count = 0

    for tweet in clean_tweets:
        score = tweet.sentiment_score

        if score != 0:
            r = (tweet.favorite_count/2 + tweet.retweet_count)/10
            if r > 10:
                r = 10

            data = {
                        'y': round((score+1)*5,1),
                        'x': str(tweet.created_at),
                        'r': 5 + r,
                        'tweet': tweet.text,
                    }

            if score < 0:
                negative_data.append(data)
            else:
                positive_data.append(data)
        else:
            neutral_count += 1

    return negative_data, positive_data, neutral_count

## =============================================================================

## Returns a touple of positive daily averages and daily negative averages of
## tweet sentiment over time
def get_daily_avgs(clean_tweets):
    positive_data = {}
    negative_data = {}
    positive_avgs = []
    negative_avgs = []

    for tweet in clean_tweets:
        day = datetime.datetime.date(tweet.created_at)

        if tweet.sentiment_score < 0:
            try:
                negative_data[day].append(tweet.sentiment_score)
            except:
                negative_data[day] = [tweet.sentiment_score]
        elif tweet.sentiment_score > 0:
            try:
                positive_data[day].append(tweet.sentiment_score)
            except:
                positive_data[day] = [tweet.sentiment_score]

    for (day, scores) in positive_data.items():
        positive_avgs.append({ 'x' : day, 'y' : (sum(scores) / len(scores)) * 10})

    for (day, scores) in negative_data.items():
        negative_avgs.append({ 'x' : day, 'y' : (sum(scores) / len(scores)) * (-10)})

    positive_avgs.sort(key=lambda entry: entry['x'])
    negative_avgs.sort(key=lambda entry: entry['x'])

    return positive_avgs, negative_avgs

## =============================================================================

## Returns a list of Tweet objects created from the given list of twitter.Status objects
def get_clean_tweets(raw_tweets, movie_title):
    clean_tweets = []
    for raw_tweet in raw_tweets:
        clean_tweet = Tweet().fillWithStatusObject(raw_tweet, movie_title)
        if clean_tweet:
            clean_tweets.append(clean_tweet)
    return clean_tweets

## =============================================================================

## Returns a list of at most 10 Tweet objects whos sentiment scores are not 0
def get_tweets_to_display(clean_tweets):
    tweets_to_display = []
    i = 0
    while i < len(clean_tweets) and len(tweets_to_display) < 20:
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

            for i in range(0, (int(tweet.retweet_count/4))):
                num_nonzero += 1
                sum_scores += score

            for i in range(0, (int(tweet.favorite_count/8))):
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
