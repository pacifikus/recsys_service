from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
    valid_token_headers: str,
    valid_request_data: dict,
) -> None:
    path = GET_RECO_PATH.format(**valid_request_data)
    with client:
        response = client.get(path, headers=valid_token_headers)
    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_json["user_id"] == valid_request_data["user_id"]
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
    valid_token_headers: str,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="first", user_id=user_id)
    with client:
        response = client.get(path, headers=valid_token_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
    unknown_model: str,
    valid_token_headers: str,
) -> None:
    path = GET_RECO_PATH.format(model_name=unknown_model, user_id=1)
    with client:
        response = client.get(path, headers=valid_token_headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_message"] == "Model not found"


def test_get_reco_with_wrong_token(
    client: TestClient,
    valid_request_data: dict,
    wrong_token_headers: str,
) -> None:
    path = GET_RECO_PATH.format(**valid_request_data)
    with client:
        response = client.get(path, headers=wrong_token_headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert (
        response.json()["errors"][0]["error_message"]
        == "Could not validate credentials"
    )


def test_get_reco_without_token(
    client: TestClient,
    valid_request_data: dict,
) -> None:
    path = GET_RECO_PATH.format(**valid_request_data)
    with client:
        response = client.get(path)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_message"] == "Not authenticated"
