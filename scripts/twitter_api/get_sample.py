# Check https://github.com/bear/python-twitter for docs on twitter package

import twitter
import yaml
import sys, getopt

def main(argv):
	## Default arg values
	searchTerm = "test"
	ntweets = 10
	filename_yaml = "testSample.yml"
	filename_json = "testSample.json"

	## Get command line arguments for search param, count, filename
	try:
		opts, args = getopt.getopt(argv,"hs:c:f:",["search=","count=","file="])
	except getopt.GetoptError:
		print("get_sample.py -s <searchparam> -c <tweetcount> -f <filename>")
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print("get_sample.py -s <searchparam> -c <tweetcount> -f <filename>")
			sys.exit()
		elif opt in ("-s","--search"):
			searchTerm = arg
		elif opt in ("-c","--count"):
			ntweets = arg
		elif opt in ("-f","--file"):
			filename = arg

	# load the API keys from api_keys.txt
	with open("api_keys.yml", 'r') as stream:
		try:
			keys = yaml.load(stream)
		except yaml.YAMLError as exc:
			print(exc)

	api = twitter.Api(consumer_key=keys['consumer_key'], consumer_secret=keys['consumer_secret'], access_token_key=keys['access_token_key'],  access_token_secret=keys['access_token_secret'])

	## Note: so far, can only get 100 tweets (measured by output line count), even when setting the
	## count to a number greater than 100. Setting the number less than 100 still gives the appropriate
	## number of returned tweets.
	tweets = api.GetSearch(term=searchTerm, count=ntweets)

	output_file_yaml = open(filename_yaml, 'w')
	output_file_json = open(filename_json, 'w')

	for tweet in tweets:
		yaml.dump(tweet, output_file_yaml, allow_unicode=True)
		output_file_json.write(tweet.AsJsonString() + "\n")

if __name__ == "__main__":
	main(sys.argv[1:])


# Remove unwanted fields from each of the Tweet objects
def filter_tweets(tweets):
	for tweet in tweets:
		tw
