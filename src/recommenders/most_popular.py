from itertools import cycle, islice

import pandas as pd

from .base import BaseRecommender


class MostPopularRecommender(BaseRecommender):
    def __init__(
        self,
        max_k=10,
        days=30,
        item_column="item_id",
        dt_column="date",
    ):
        self.max_k = max_k
        self.days = days
        self.item_column = item_column
        self.dt_column = dt_column
        self.recommendations = []

    def fit(self, df):
        min_date = df[self.dt_column].max().normalize() - pd.DateOffset(
            days=self.days
        )
        self.recommendations = (
            df.loc[df[self.dt_column] > min_date, self.item_column]
            .value_counts()
            .head(self.max_k)
            .index.values
        )
        return self

    def recommend(self, users=None, n=10):
        recs = self.recommendations[:n]
        if users is None:
            return recs
        return list(islice(cycle([recs]), len(users)))
