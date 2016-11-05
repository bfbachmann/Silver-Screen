import nltk.data


class Lexicon(object):
    def __init__(self, lexicon_file="lexicon_done.txt"):
        self.lexicon_file = nltk.data.load(lexicon_file)
        self.lexicon = self.convert_to_dictionary()

    def convert_to_dictionary(self):
        """
        Converts the lexicon text file into a dictionary
        """
        lexicon_dictionary = {}
        for line in self.lexicon_file.split('\n'):
            (word, measure) = line.strip().split('\t')[0:2]
            lexicon_dictionary[word] = float(measure)

        return lexicon_dictionary
