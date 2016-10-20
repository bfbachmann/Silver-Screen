class Movie(object):
    """  """
    def __init__(self, title, year):
        self.title = title
        self.year = year
        self.img_url = "" #URL of the image of the movie
        # external links related to the movie
        #such as IMBD and Rotten Tomatoes
        self.links = {}
        self.director = ""
        self.cast = []
        self.genre = ""
        self.revenue = 0

    def addactor(self, new_actor):
        #Add new actor to the cast array
        self.cast.append(new_actor)

    def addlink(self, desc, link):
        #Add new link to the dictionary links
        #desc is the name of the link
        #link is the URL
        self.links[desc] = link
