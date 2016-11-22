# Check https://github.com/bear/python-twitter for docs on twitter package
import omdb
import twitter
import pprint
import yaml

# load the API keys from api_keys.txt
with open("api_keys.yml", 'r') as stream:
    try:
        keys = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

api = twitter.Api(consumer_key=keys['consumer_key'], consumer_secret=keys['consumer_secret'], access_token_key=keys['access_token_key'],  access_token_secret=keys['access_token_secret'])

searchTerm = "hello"
tweets = api.GetSearch(term=searchTerm)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(tweets)
