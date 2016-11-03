import sys
import math
import re
import string
from itertools import product
import nltk.data

'''
ALGORITHM CONSTANTS
'''

# valence score modifiers based on the use of adverbs (positive or negative) THESE ARE EXPERIMENTAL
SCORE_INCREASE = 0.5
SCORE_DECREASE = -0.5

# valence score increase based on using capitals to emphasize a word THIS IS EXPERIMENTAL
CAPS_INCREASE = 1.00

# valence score increase based on exclamation points or question marks THIS IS EXPERIMENTAL
EXCLAMATION_INCREASE = 0.25
QUESTION_INCREASE = 0.1

# sentiment modifier for use of a negation (EXPERIMENTAL)
NEGATION_MODIFIER = -1.00

# regex function to remove punctuation from a string
PUNCTUATION_REMOVER = re.compile('[%s]' % re.escape(string.punctuation))

# list of punctuation we see in twitter (VERY UNFINISHED)
PUNCTUATION_LIST = ["...","..",".", "!", "?", ",", ";", ":", "-", "'", "\"",
             "!!", "!!!", "??", "???", "?!?", "!?!", "?!?!", "!?!?"]

# list of words which negate the meanings that follow, with some variations in spelling
NEGATION_DICTIONARY = \
["aint", "arent", "cannot", "cant", "couldnt", "darent", "didnt", "doesnt",
 "ain't", "aren't", "can't", "couldn't", "daren't", "didn't", "doesn't",
 "dont", "hadnt", "hasnt", "havent", "isnt", "mightnt", "mustnt", "neither",
 "don't", "hadn't", "hasn't", "haven't", "isn't", "mightn't", "mustn't",
 "neednt", "needn't", "never", "none", "nope", "nor", "not", "nothing", "nowhere",
 "oughtnt", "shant", "shouldnt", "uhuh", "wasnt", "werent",
 "oughtn't", "shan't", "shouldn't", "uh-uh", "wasn't", "weren't",
 "without", "wont", "wouldnt", "won't", "wouldn't", "rarely", "seldom", "despite"]

'''
these are adverbs which express the degree to which the word they modify applies
the scores should be worked out on an individual basis, as well as the dictionary itself (WORK IN PROGRESS)

here is a full list of the words:
http://en.wiktionary.org/wiki/Category:English_degree_adverbs
'''

DEGREE_DICTIONARY = \
{"100 percent": SCORE_INCREASE, "a good deal": SCORE_INCREASE, "a great deal": SCORE_INCREASE, "a lot": SCORE_INCREASE,
 "aboundingly": SCORE_INCREASE, "absolutely": SCORE_INCREASE, "absurdly": SCORE_INCREASE, "abundantly": SCORE_INCREASE,
 "admirably": SCORE_INCREASE, "alarmingly": SCORE_INCREASE, "amazingly": SCORE_INCREASE,
 "astronomically": SCORE_INCREASE, "awfully": SCORE_INCREASE, "breathtakingly": SCORE_INCREASE,
 "clearly": SCORE_INCREASE, "completely": SCORE_INCREASE, "considerably": SCORE_INCREASE, "crazy": SCORE_INCREASE,
 "damn": SCORE_INCREASE, "damned": SCORE_INCREASE, "darn": SCORE_INCREASE, "darned": SCORE_INCREASE,
 "decidedly": SCORE_INCREASE, "deeply": SCORE_INCREASE, "deservedly": SCORE_INCREASE, "downright": SCORE_INCREASE,
 "dreadfully": SCORE_INCREASE, #up to here so far
 "effing": SCORE_INCREASE, "enormously": SCORE_INCREASE,
 "entirely": SCORE_INCREASE, "especially": SCORE_INCREASE, "exceptionally": SCORE_INCREASE, "extremely": SCORE_INCREASE,
 "fabulously": SCORE_INCREASE, "flipping": SCORE_INCREASE, "flippin": SCORE_INCREASE,
 "fricking": SCORE_INCREASE, "frickin": SCORE_INCREASE, "frigging": SCORE_INCREASE, "friggin": SCORE_INCREASE, "fully": SCORE_INCREASE, "fucking": SCORE_INCREASE,
 "greatly": SCORE_INCREASE, "hella": SCORE_INCREASE, "highly": SCORE_INCREASE, "hugely": SCORE_INCREASE, "incredibly": SCORE_INCREASE,
 "intensely": SCORE_INCREASE, "majorly": SCORE_INCREASE, "more": SCORE_INCREASE, "most": SCORE_INCREASE, "particularly": SCORE_INCREASE,
 "purely": SCORE_INCREASE, "quite": SCORE_INCREASE, "really": SCORE_INCREASE, "remarkably": SCORE_INCREASE,
 "so": SCORE_INCREASE, "substantially": SCORE_INCREASE,
 "thoroughly": SCORE_INCREASE, "totally": SCORE_INCREASE, "tremendously": SCORE_INCREASE,
 "uber": SCORE_INCREASE, "unbelievably": SCORE_INCREASE, "unusually": SCORE_INCREASE, "utterly": SCORE_INCREASE,
 "very": SCORE_INCREASE,
 "almost": SCORE_DECREASE, "barely": SCORE_DECREASE, "hardly": SCORE_DECREASE, "just enough": SCORE_DECREASE,
 "kind of": SCORE_DECREASE, "kinda": SCORE_DECREASE, "kindof": SCORE_DECREASE, "kind-of": SCORE_DECREASE,
 "less": SCORE_DECREASE, "little": SCORE_DECREASE, "marginally": SCORE_DECREASE, "occasionally": SCORE_DECREASE, "partly": SCORE_DECREASE,
 "scarcely": SCORE_DECREASE, "slightly": SCORE_DECREASE, "somewhat": SCORE_DECREASE,
 "sort of": SCORE_DECREASE, "sorta": SCORE_DECREASE, "sortof": SCORE_DECREASE, "sort-of": SCORE_DECREASE}

'''
NOTE: if you come up with an idea for a module of something we should check in the algorithm, this is  good place to put it

ALGORITHM IDEAS TO BE IMPLEMENTED
1. idioms
2. urban dictionary implementation?
3. some kind Sentiment Classifier package implementation
4.s
...

'''


'''
ALGORITHM METHODS
'''


def demo(text):
    analyzer = SentimentScorer()
    scores = analyzer.polarity_scores(text)
    print(scores['sentiment'])
    print()


def normalize(score, alpha=15):
    """
    Normalize the score to be between -1 and 1 using an alpha that
    approximates the max expected value (EXPERIMENTAL!!!)

    :param score: the calculated polarity of the list of words
    :param alpha: predetermined alpha value that approximates the maximum expected value
    :return: normalized score between -1 and 1
    """

    return score / math.sqrt((score * score) + alpha)


def negate(input_words, include_nt=True):
    """
    determines if input contains negation words

    :param input_words: the list of words that we are checking
    :param include_nt: a boolean to check if any of the words end in 'n't'
    :return: true if there are negation words, false if not
    """

    neg_words = []
    neg_words.extend(NEGATION_DICTIONARY)

    for word in neg_words:
        if word in input_words:
            return True
    if include_nt:
        for word in input_words:
            if "n't" in word:
                return True
    if "least" in input_words:      # this checks to see if the person uses "least good" or something, makes sure it's not "at least"
        i = input_words.index("least")
        if i > 0 and input_words[i-1] != "at":
            return True

    return False


def alter_valence(word, valence, is_capitalized):
    """
    checks whether the word that precedes a given word will alter its valence score
    positively, negatively, or negate it entirely.

    :param word: one word in the list of words in a tweet
    :param valence: current valence score of the word
    :param is_capitalized: truth value of whether the word is capitalized
    :return: a modifier to multiply the valence score by
    """

    modifier = 0.0
    word_lower = word.lower()

    if word_lower in DEGREE_DICTIONARY:
        modifier = DEGREE_DICTIONARY[word_lower]
        if valence < 0:
            modifier *= -1
        # checks if word is capitalized (while others aren't)
        if word.isupper() and is_capitalized:
            if valence > 0:
                modifier += CAPS_INCREASE
            else:
                modifier -= CAPS_INCREASE

    return modifier


def capitalized(words):
    """
    Checks if specific words are capitalized or the whole tweet,
    in order to determine whether we should differentiate the word based on its capitalization

    :param list words: the list of words to inspect
    :returns: True if some but not all of the words in the list are capitalized,
    False if none or all are capitalized
    """
    emphasis = False
    capitalized_words = 0

    for word in words:
        if word.isupper():
            capitalized_words += 1
    cap_differential = len(words) - capitalized_words
    if 0 < cap_differential < len(words):
        emphasis = True

    return emphasis


class SentimentScorer(object):
    """
    Gives an intensity score to the inputted tweet.
    """
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

    def polarity_scores(self, text):
        """
        This method returns the sentiment value of the given text.

        :param text: input text
        :return: returns a float value which represents the sentiment score of the inputted text
        """

        analyzer = SentimentAnalyzer(text)
        # text, words_and_symbols, is_capitalized = self.preprocess(text)

        sentiments = []
        words_and_symbols = analyzer.words_and_symbols

        for item in words_and_symbols:
            valence = 0
            i = words_and_symbols.index(item)
            if item.lower() in DEGREE_DICTIONARY:
                sentiments.append(valence)
                continue

            sentiments = self.sentiment_polarity(valence, analyzer, item, i, sentiments)

        sentiments = self._contains_but(words_and_symbols, sentiments)

        return self.score_valence(sentiments, text)

    def sentiment_polarity(self, valence, analyzer, item, i, sentiments):
        """
        applies a variety of modifications to the raw sentiment scores of
        the words in the tweet based on context

        :param valence: current valence score
        :param analyzer: given sentiment text class we are analyzing
        :param item: a single element of the list of words
        :param i: index of that element
        :param sentiments: list of sentiment scores of each word
        :return: an updated list of sentiment scores
        """
        is_capitalized = analyzer.is_capitalized
        words_and_symbols = analyzer.words_and_symbols
        item_is_lowercase = item.lower()

        if item_is_lowercase in self.lexicon:
            # get the sentiment valence
            valence = self.lexicon[item_is_lowercase]

            # check if word is capitalized (while others aren't)
            if item.isupper() and is_capitalized:
                if valence > 0:
                    valence += CAPS_INCREASE
                else:
                    valence -= CAPS_INCREASE

            for predecessor_index in range(0, 3):
                if i > predecessor_index and words_and_symbols[i-(predecessor_index+1)].lower() not in self.lexicon:
                    # decreases the score modification of preceding words and symbols
                    # (excluding the ones that IMMEDIATELY precede the item) based
                    # on their distance from the current word
                    s = alter_valence(words_and_symbols[i-(predecessor_index+1)], valence, is_capitalized)
                    if predecessor_index == 1 and s != 0:
                        s *= 0.95
                    if predecessor_index == 2 and s != 0:
                        s *= 0.9
                    valence += s
                    valence = self._contains_never(valence, words_and_symbols, predecessor_index, i)

                    # this where we could do an idiom check of some kind

            valence = self._contains_least(valence, words_and_symbols, i)

        sentiments.append(valence)

        return sentiments

    def _contains_least(self, valence, words_and_symbols, i):
        """
        checks to see if the current word is preceded by variations on "least"
        negatively impacts score

        :param valence: current valence score
        :param words_and_symbols: list of words in the tweet
        :param i: current index
        :return: updated valence score
        """
        # check for negation case using "least"
        if i > 1 and words_and_symbols[i-1].lower() not in self.lexicon \
           and words_and_symbols[i-1].lower() == "least":
            if words_and_symbols[i-2].lower() != "at" and words_and_symbols[i-2].lower() != "very":
                valence *= NEGATION_MODIFIER
        elif i > 0 and words_and_symbols[i-1].lower() not in self.lexicon and words_and_symbols[i-1].lower() == "least":
            valence *= NEGATION_MODIFIER

        return valence

    def _contains_but(self, words_and_symbols, sentiments):
        """
        checks for the word 'but' in the tweet, and alters
        the following words' scores accordingly

        :param words_and_symbols: list of the words in the tweet
        :param sentiments: list of current sentiment scores
        :return: updated sentiment scores
        """
        if 'but' in words_and_symbols or 'BUT' in words_and_symbols:
            try:
                but_index = words_and_symbols.index('but')
            except ValueError:
                but_index = words_and_symbols.index('BUT')
            for sentiment in sentiments:
                sentiment_index = sentiments.index(sentiment)
                if sentiment_index < but_index:
                    sentiments.pop(sentiment_index)
                    sentiments.insert(sentiment_index, sentiment*0.5)  # modifier value seems sensible to me
                elif sentiment_index > but_index:
                    sentiments.pop(sentiment_index)
                    sentiments.insert(sentiment_index, sentiment*1.5)  # modifier value seems sensible to me

        return sentiments

    def _contains_never(self, valence, words_and_symbols, predecessor_index, i):
        """
        adjusts the score based on a preceding usage of the word "never"

        :param valence: current valence score
        :param words_and_symbols: list of words in the tweet
        :param predecessor_index: index of the words preceding it
        :param i: current word's index
        :return: updated valence score
        """
        if predecessor_index == 0:
            if negate([words_and_symbols[i-1]]):
                valence *= NEGATION_MODIFIER
        if predecessor_index == 1:
            if words_and_symbols[i-2] == "never" and\
               (words_and_symbols[i-1] == "so" or
                words_and_symbols[i-1] == "this"):
                valence *= 1.5                              # modifier value seems sensible to me
            elif negate([words_and_symbols[i-(predecessor_index+1)]]):
                valence *= NEGATION_MODIFIER
        if predecessor_index == 2:
            if words_and_symbols[i-3] == "never" and \
               (words_and_symbols[i-2] == "so" or words_and_symbols[i-2] == "this") or \
               (words_and_symbols[i-1] == "so" or words_and_symbols[i-1] == "this"):
                valence *= 1.25
            elif negate([words_and_symbols[i-(predecessor_index+1)]]):
                valence *= NEGATION_MODIFIER

        return valence

    def _punctuation_boost(self, sum_s, text):
        # add emphasis from exclamation points and question marks
        exclamation_booster = self._exclamation_boost(text)
        question_booster = self._question_boost(text)
        punc_booster = exclamation_booster + question_booster

        return punc_booster

    def _exclamation_boost(self, text):
        # check for added emphasis resulting from exclamation points (up to 4 of them)
        exclamation_count = text.count("!")
        if exclamation_count > 4:
            exclamation_count = 4

        exclamation_booster = exclamation_count * EXCLAMATION_INCREASE

        return exclamation_booster

    def _question_boost(self, text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        question_booster = 0
        if qm_count > 1:
            if qm_count <= 3:
                question_booster = qm_count * QUESTION_INCREASE
            else:
                question_booster = 1.00

        return question_booster

    def _organize_scores(self, sentiments):
        # want separate positive versus negative sentiment scores
        positive_score = 0.0
        negative_score = 0.0
        neutral_words = 0

        for sentiment_score in sentiments:
            if sentiment_score > 0:
                positive_score += (float(sentiment_score) + 1) # compensates for neutral words that are counted as 1
            if sentiment_score < 0:
                negative_score += (float(sentiment_score) - 1) # when used with math.fabs(), compensates for neutrals
            if sentiment_score == 0:
                neutral_words += 1

        return positive_score, negative_score, neutral_words

    def score_valence(self, sentiments, text):
        if sentiments:
            sentiment_sum = float(sum(sentiments))

            # compute and consider emphasis from the punctuation of the text
            punc_booster = self._punctuation_boost(sentiment_sum, text)
            if sentiment_sum > 0:
                sentiment_sum += punc_booster
            elif sentiment_sum < 0:
                sentiment_sum -= punc_booster

            compound = normalize(sentiment_sum)
            # discriminate between positive, negative and neutral sentiment scores
            positive_score, negative_score, neutral_words = self._organize_scores(sentiments)

            if positive_score > math.fabs(negative_score):
                positive_score += punc_booster
            elif positive_score < math.fabs(negative_score):
                negative_score -= punc_booster

            total = positive_score + math.fabs(negative_score) + neutral_words
            positivity = math.fabs(positive_score / total)
            negativity = math.fabs(negative_score / total)
            neutrality = math.fabs(neutral_words / total)

        else:
            compound = 0.0
            positivity = 0.0
            negativity = 0.0
            neutrality = 0.0

        sentiment_dictionary = \
            {"negativity": round(negativity, 3),
             "neutrality": round(neutrality, 3),
             "positivity": round(positivity, 3),
             "sentiment": round(compound, 4)}

        return sentiment_dictionary


class SentimentAnalyzer(object):
    """
    Identify sentiment-relevant string-level properties of input text.
    """
    def __init__(self, text):
        if not isinstance(text, str):
            text = str(text.encode('utf-8'))
        self.text = text
        self.words_and_symbols = self._words_and_symbols()
        # doesn't separate words from\
        # adjacent punctuation (keeps emoticons & contractions)
        self.is_capitalized = capitalized(self.words_and_symbols)

    def _word_punctuation_dictionary(self):
        """
        creates a dictionary whose key is the text
        and whose value is the text without punctuation
        i.e.: "gross,: gross"
        or "sentiment: sentiment"

        return: a dictionary with keys of words w/ punctuation and values of that word without punctuation
        """
        words_only = PUNCTUATION_REMOVER.sub('', self.text).split()
        # remove indefinite article
        words_only = set(w for w in words_only if len(w) > 1)
        # product is essentially a nested for loop // or the cartesian product from itertools package
        punc_before = {''.join(p): p[1] for p in product(PUNCTUATION_LIST, words_only)}
        punc_after = {''.join(p): p[0] for p in product(words_only, PUNCTUATION_LIST)}
        words_punc_dict = punc_before
        words_punc_dict.update(punc_after)

        return words_punc_dict

    def _words_and_symbols(self):
        """
        Removes preceding and following punctuation
        Leaves contractions and most emoticons, but does not preserve letter/punctuation emoticons like :D

        return: list of words
        """
        word_list = self.text.split()
        words_punc_dict = self._word_punctuation_dictionary()
        word_list = [w for w in word_list if len(w) > 1]

        for i, w in enumerate(word_list):
            if w in words_punc_dict:
                word_list[i] = words_punc_dict[w]

        return word_list


if __name__ == '__main__':
    demo("I hate Michael Bay films, and this one sucks")
    demo("ALSO. Go see @moonlightmov this weekend. It is artful food for your soul. At a time when so many of us need to be lovingly nourished.")
    demo("Moonlight is the best movie &unlike me u wont have a woman behind u coughing, gagging on popcorn,saying\"here they go again\"4 every gay scene")
    demo("moonlight is a not great movie")
