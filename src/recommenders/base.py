import pickle
from abc import abstractmethod


class BaseRecommender:
    @abstractmethod
    def fit(self, df):
        ...

    @abstractmethod
    def recommend(self, users=None, n=10):
        ...

    def save(self, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)
