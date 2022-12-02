import dill
import pandas as pd


class UserKNN:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.users_mapping, self.users_inv_mapping = None, None
        self.__load_models()
        self.train = self.__load_train_data()
        self.mapper = self.__generate_implicit_recs_mapper(
            N=self.config['user_knn']['n_users'],
        )

    def recommend(self, user_ids, n_recs=10):
        recs = pd.DataFrame({
            'user_id': user_ids
        })

        recs['similar_user_id'], recs['similarity'] = zip(
            *recs['user_id'].map(self.mapper)
        )
        recs = recs.set_index('user_id').apply(pd.Series.explode).reset_index()
        recs = recs[recs['user_id'] != recs['similar_user_id']]
        recs = self.__join_watched(recs)

        # recs['rank'] = recs.groupby('user_id').cumcount() + 1
        # recs = recs[recs['rank'] < n_recs + 1]
        return recs

    def __generate_implicit_recs_mapper(self, N):
        def _recs_mapper(user):
            user_id = self.users_mapping[user]
            recs = self.model.similar_items(user_id, N=N)
            return (
                [self.users_inv_mapping[user] for user, _ in recs],
                [sim for _, sim in recs],
            )

        return _recs_mapper

    def __join_watched(self, recs_df):
        similar_users_items = [
            self.train[key] for key in recs_df['similar_user_id'].values
        ]
        return list(set(similar_users_items))

    def __load_models(self):
        try:
            with open(self.config['user_knn']['model_path'], 'rb') as f:
                self.model = dill.load(f)

            with open(self.config['user_knn']['users_mapping_path'],
                      'rb') as f:
                self.users_mapping = dill.load(f)

            with open(
                self.config['user_knn']['users_inv_mapping_path'],
                'rb',
            ) as f:
                self.users_inv_mapping = dill.load(f)
        except FileNotFoundError:
            print('models folder is empty...')

    def __load_train_data(self):
        user_item_dict = None
        try:
            interactions = pd.read_csv(
                self.config['data']['interactions_path'])
            interactions.rename(
                columns={
                    'last_watch_dt': 'datetime',
                    'total_dur': 'weight',
                },
                inplace=True,
            )

            interactions['datetime'] = pd.to_datetime(interactions['datetime'])
            interactions['rank'] = interactions.groupby(
                'user_id').cumcount() + 1
            interactions = interactions[interactions['rank'] < 11]
            user_item_dict = interactions.set_index('user_id')[
                'item_id'].to_dict()
        except FileNotFoundError:
            print('data folder is empty...')
        return user_item_dict
