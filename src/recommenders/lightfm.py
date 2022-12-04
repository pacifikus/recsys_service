import dill
import numpy as np


class LightFMWrapper:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.users_mapping, self.items_inv_mapping = None, None
        self.__load_models()

    def recommend(self, user_id, n_recs=10):
        user_inner_idx = self.users_mapping[user_id[0]]
        items_embedding, user_embedding = self.__get_embeddings(user_inner_idx)
        scores = items_embedding @ user_embedding
        top_score_ids = scores.argsort()[-n_recs:][::-1]
        items_to_recommend = [
            self.items_inv_mapping[item] for item in top_score_ids if
            item in self.items_inv_mapping
        ]
        return items_to_recommend

    def __get_embeddings(self, user_inner_idx):
        user_biases, user_embedding = (
            self.model.get_user_representations()[0][user_inner_idx],
            self.model.get_user_representations()[1][user_inner_idx],
        )
        items_biases, items_embedding = self.model.get_item_representations()
        items_embedding = items_embedding[:len(self.items_inv_mapping), :]
        items_biases = items_biases[:len(self.items_inv_mapping)]
        user_embedding = np.hstack(
            (
                user_biases, np.ones(user_biases.size),
                user_embedding,
            ),
        )
        items_embedding = np.hstack(
            (
                np.ones((items_biases.size, 1)),
                items_biases[:, np.newaxis],
                items_embedding,
            ),
        )
        return items_embedding, user_embedding

    def __load_models(self):
        try:
            with open(self.config['lightfm']['model_path'], 'rb') as f:
                self.model = dill.load(f)

            with open(
                self.config['lightfm']['users_mapping_path'],
                'rb',
            ) as f:
                self.users_mapping = dill.load(f)

            with open(
                self.config['lightfm']['items_inv_mapping_path'],
                'rb',
            ) as f:
                self.items_inv_mapping = dill.load(f)
        except FileNotFoundError:
            print('models folder is empty...')
