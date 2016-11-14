class word_detector(object):

    def __init__(self):
    
        #Lists are sourced from:
        with open("uncommon_wordlist.txt", 'r',encoding="gb18030") as f:
            self.uncommon_wordlist = f.readlines()  #list containing top 2000-5000 words in english language
        self.uncommon_wordlist = [word.replace('\n','') for word in self.uncommon_wordlist]
        
        with open("common_wordlist.txt", 'r',encoding="gb18030") as f:
            self.common_wordlist = f.readlines()    #list containing top 2000 words in english language
        self.common_wordlist = [word.replace('\n','') for word in self.common_wordlist]
        
    def __cleanSearchTerm(self, word):
        word = word.lower()
        return word.split()
        
                
    def __searchLists(self, term):
        for word in self.common_wordlist:
            if (term == word):
                return 1
        for word in self.uncommon_wordlist:
            if (term == word):
                return 3
        return 5

    def commonTitleChecker(self, search_term):
        """
        :param searchterm: movie title to check for in file containing common words
        :return boolean whether the movie title was found
        
        A title is usually considered uncommon when it has 1 or more words not in either wordlist (e.g X-Men) or 3 or more uncommon words (e.g. Miss Peregrine's Home for Peculiar Children)
        
        Title commoness scoring system: 
        For every word in the title the score is increased by 1
        For every common word in the title the score is increased by 1
        For every uncommon word in the title the score is increased by 3
        For all other words the score is increased by 10
        If the total score exceeds 10 the title is uncommon
        
        """
        scoreTotal = 1
        search_term = self.__cleanSearchTerm(search_term)
        for word in search_term:
            scoreTotal += 1;
            scoreTotal += self.__searchLists(word)
            
            
        print("score is: ", end="")
        print(scoreTotal)
        return (scoreTotal < 10)
    


    
    
    