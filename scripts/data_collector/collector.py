import omdb

class OMDbAPI(object):

    def __init__(self):
        self.recentSearches = {}

    # @params:
    #       title: a string holding the title of the movie
    # @returns:
    #       movie: if at least one movie with a similar title is found, this is a Movie object
    #              created from the most relevant result returned by OMDb, otherwise it is None
    def search(self, title, year=None):
        # search for all movies with similar titles
        matching_movies = omdb.search_movie(title)
        self.recentSearches.update({title:matching_movies})

        #For now, only return most popular movie

        highestIMDB = 0

        if matching_movies:
            movie = matching_movies.pop(0)

            response = omdb.request(i=movie.imdb_id, tomatoes=True, type='movie').json()
            return response
        return None


omdb_api = OMDbAPI()

output_file = open("movie_titles.txt", 'w')

with open('popular_movies.txt') as titles:
    for i, line in enumerate(titles):
        movie = omdb_api.search(line)
        if movie is not None:
            print(movie['Title'])
            output_file.write(movie['Title'] + '\n')
