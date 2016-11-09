from common_word_detector import word_detector

def main():

    print(word_detector().commonTitleChecker('a'))
    print(word_detector().commonTitleChecker('afsafsd'))
    print(word_detector().commonTitleChecker('Twilight'))
    print(word_detector().commonTitleChecker('twilight'))

if __name__ == "__main__": main()