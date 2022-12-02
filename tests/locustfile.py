import os
import random

from locust import HttpUser, between, task


class LoadTestUser(HttpUser):
    wait_time = between(0.5, 2)

    @task
    def get_recos(self):
        model_name = "userknn"
        user_id = random.randint(1, 100000)
        valid_token_headers = {
            "Authorization": f"Bearer {os.getenv('BOT_TOKEN')}"
        }
        self.client.get(
            f"reco/{model_name}/{user_id}",
            headers=valid_token_headers,
        )
