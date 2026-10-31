from collections.abc import Callable, Iterator
from typing import Any
from uuid import uuid4

import pytest

from tests.api_client import ApiClient


@pytest.fixture
def api_client() -> Iterator[ApiClient]:
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture
def user_data() -> dict[str, str]:
    unique_id = uuid4().hex
    return {
        "email": f"diplom-{unique_id}@example.com",
        "password": f"Pass-{unique_id}!",
        "name": f"Diplom User {unique_id[:8]}",
    }


@pytest.fixture
def cleanup_user(
    api_client: ApiClient,
) -> Iterator[Callable[[str], None]]:
    access_tokens: list[str] = []

    def register_for_cleanup(access_token: str) -> None:
        access_tokens.append(access_token)

    yield register_for_cleanup

    for access_token in access_tokens:
        response = api_client.request("DELETE", "/auth/user", token=access_token)
        assert response.status_code in (200, 202), response.text
        assert response.json().get("success") is True, response.text


@pytest.fixture
def registered_user(
    api_client: ApiClient,
    user_data: dict[str, str],
    cleanup_user: Callable[[str], None],
) -> dict[str, Any]:
    response = api_client.request("POST", "/auth/register", payload=user_data)
    assert response.status_code == 200, response.text
    response_data = response.json()
    cleanup_user(response_data["accessToken"])
    assert response_data.get("success") is True, response.text
    return {"payload": user_data, **response_data}


@pytest.fixture
def ingredients(api_client: ApiClient) -> list[dict[str, Any]]:
    response = api_client.request("GET", "/ingredients")
    assert response.status_code == 200, response.text
    response_data = response.json()
    assert response_data.get("success") is True, response.text
    assert response_data.get("data"), response.text
    return response_data["data"]
