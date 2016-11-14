from common_word_detector import word_detector

def main():

    print("Twilight")
    print(word_detector().commonTitleChecker('Twilight'))
    print("Home Alone")
    print(word_detector().commonTitleChecker('Home Alone'))
    print("Inception")
    print(word_detector().commonTitleChecker('Inception'))
    print("Hop")
    print(word_detector().commonTitleChecker('Hop'))
    print("The Edge of Tomorrow ")
    print(word_detector().commonTitleChecker('The edge of Tomorrow'))
    print("Pulp Fiction")
    print(word_detector().commonTitleChecker('Pulp Fiction'))
    print("Magnificant Seven")
    print(word_detector().commonTitleChecker('Magnificant Seven'))
    print("Ghost in the Shell")
    print(word_detector().commonTitleChecker('Ghost in the Shell'))

if __name__ == "__main__": main()