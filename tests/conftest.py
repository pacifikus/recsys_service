# pylint: disable=redefined-outer-name
import os
import random
import string

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from service.api.app import create_app
from service.settings import ServiceConfig, get_config


@pytest.fixture
def service_config() -> ServiceConfig:
    return get_config()


@pytest.fixture
def app(
    service_config: ServiceConfig,
) -> FastAPI:
    app = create_app(service_config)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def unknown_model() -> str:
    return "".join(random.choices(string.ascii_letters, k=7))


@pytest.fixture
def wrong_token_headers():
    token = "".join(random.choices(string.ascii_letters, k=126))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_token_headers():
    return {"Authorization": f"Bearer {os.getenv('BOT_TOKEN')}"}


@pytest.fixture
def valid_request_data():
    return {"model_name": "first", "user_id": 1}
