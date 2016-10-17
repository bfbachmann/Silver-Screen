import urllib
import json
import sys

title = sys.argv[1]
nurl = "http://www.omdbapi.com/?t=" + title + "&y=&plot=short&r=json"
response = urllib.urlopen(nurl)
data = json.loads(response.read())


print data['Title']
print data['Year']
print data['Poster']
print data['Director']
print data['Actors']
print data['Genre']
print nurl
