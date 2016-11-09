class word_detector(object):

    def __init__(self):
        with open("common_wordlist.txt", 'r') as f:
            self.common_wordlist = f.readlines()
            
            
        self.common_wordlist = [word.replace('\n','') for word in self.common_wordlist]
        for word in self.common_wordlist:
            word = word.replace("\n", "")

    def commonTitleChecker(self, search_term):
        """
        :param searchterm: movie title to check for in file containing common words
        :return boolean whether the movie title was found
        """
        if len(line.split()) > 1: # has more than 1 word
            return False
        
        search_term = search_term.lower()
        for word in self.common_wordlist:
            if (search_term == word):
                return True
            elif (search_term < word):
                return False
        return False