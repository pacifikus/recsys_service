import pandas as pd

from src.recommenders import MostPopularRecommender

data_file_path = "data/kion_train/interactions.csv"
date_column = "last_watch_dt"
models_path = "models"
interactions_df = pd.read_csv(data_file_path, parse_dates=[date_column])


def simple_split(df, date_column_name):
    train_df = df[interactions_df[date_column_name] < df[date_column_name].max()]
    test_df = df[interactions_df[date_column_name] == df[date_column_name].max()]
    return train_df, test_df


train, test = simple_split(interactions_df, date_column)
model = MostPopularRecommender(days=7, dt_column=date_column)
model.fit(train)
model.save(f"{models_path}/most_popular.pkl")
