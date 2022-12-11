import dill
import pandas as pd


class HybridModelrapper:
    def __init__(self, config):
        self.config = config
        self.ranker = None
        self.ranker_data = None
        self.__load_models()

    def recommend_all(self):
        preds = self.ranker.predict(
            self.ranker_data.drop(columns=["user_id", "item_id"])
        )
        self.ranker_data["score"] = preds
        self.ranker_data["rank"] = self.ranker_data.groupby(
            "user_id"
        ).cumcount() + 1
        self.ranker_data = self.ranker_data[self.ranker_data["rank"] < 11]
        self.ranker_data.sort_values(
            by=["user_id", "score"],
            ascending=[True, False],
            inplace=True,
        )

    def recommend(self, user_id, n=10):
        df = self.ranker_data[self.ranker_data["user_id"] == user_id]
        return df["item_id"].values

    def get_default_values(self):
        return {
            "user_hist": 0,
            "item_pop": self.ranker_data["item_pop"].median(),
            "item_avg_hist": self.ranker_data["item_avg_hist"].median(),
            "male_pop": self.ranker_data["male_pop"].median(),
            "female_pop": self.ranker_data["female_pop"].median(),
            "user_avg_pop": self.ranker_data["user_avg_pop"].median(),
            "user_last_pop": self.ranker_data["user_last_pop"].median(),
            "als_score": self.ranker_data["als_score"].min() - 0.01,
            "als_rank": self.ranker_data["als_rank"].max() + 1,
            "lfm_score": self.ranker_data["lfm_score"].min() - 0.01,
            "lfm_rank": self.ranker_data["lfm_rank"].max() + 1,
            "pop_score": self.ranker_data["pop_score"].min() - 0.01,
            "pop_rank": self.ranker_data["pop_rank"].max() + 1,
        }

    def __load_models(self):
        try:
            with open(self.config["hybrid"]["ranker"], "rb") as f:
                self.ranker = dill.load(f)

            self.ranker_data = pd.read_csv(
                self.config["hybrid"]["ranker_data"]
            )
            default_values = self.get_default_values()
            self.ranker_data.fillna(default_values, inplace=True)
            self.users = self.ranker_data["user_id"].unique()
            self.recommend_all()
        except FileNotFoundError:
            print("models folder is empty...")
