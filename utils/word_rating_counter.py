"""
Source: https://svn.python.org/projects/python/trunk/Lib/collections.py
"""
import collections


class WordRatingCounter(collections.Counter):
    def __init__(self, df):
        assert 'Rating' in df.columns and 'tokens' in df.columns
        self.sorted = []
        self.update([(r, x) for r, t in zip(df.Rating, df.tokens) for x in t])

    def __missing__(self, key):
        return (0, 0, 0, 0)

    def ratings_pos(self, n):
        return list(map(lambda x: x[0], filter(lambda x: x[1][2] > 3, self.sorted)))[:n]

    def ratings_neg(self, n):
        return list(map(lambda x: x[0], filter(lambda x: x[1][2] <= 3, self.sorted)))[:n]

    def _score(self, count, rating):
        return count * max(rating, 6-rating)**2

    def update(self, iterable):
        # iterable = (rating, word)
        for r, w in iterable:
            count_new = self[w][0]+1
            rating_new = self[w][1]+r
            self[w] = (count_new, rating_new, rating_new/count_new, self._score(count_new, rating_new))
        self.sorted = sorted(self.items(), key=lambda x: x[1][3], reverse=True)
