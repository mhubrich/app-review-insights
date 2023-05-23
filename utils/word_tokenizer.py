from nltk import word_tokenize, ngrams
from nltk.corpus import stopwords
import string


class WordTokenizer:
    def __init__(self, language, blacklist=None):
        self.sw = stopwords.words(language)
        if blacklist:
            self.sw += blacklist

    def remove_punctuation(self, text):
        return text.translate(str.maketrans('', '', string.punctuation))

    def remove_stopwords(self, text):
        return [x for x in text if x not in self.sw]

    def tokenize(self, text, n=1):
        text = self.remove_punctuation(text)
        tokens = word_tokenize(text)
        tokens = self.remove_stopwords(tokens)
        if n > 1:
            tokens += [' '.join(x) for i in range(2, n+1) for x in ngrams(tokens, i)]
        return set(tokens)
