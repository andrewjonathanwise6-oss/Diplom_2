from collections.abc import Callable, Iterator
from typing import Any

import pytest

from tests.api_client import ApiClient
from tests.helpers import delete_user, get_ingredients, new_user_data, register_user


@pytest.fixture
def api_client() -> Iterator[ApiClient]:
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture
def user_data() -> dict[str, str]:
    return new_user_data()


@pytest.fixture
def cleanup_user(api_client: ApiClient) -> Iterator[Callable[[str], None]]:
    access_tokens: list[str] = []

    def register_for_cleanup(access_token: str) -> None:
        access_tokens.append(access_token)

    yield register_for_cleanup

    for access_token in access_tokens:
        delete_user(api_client, access_token)


@pytest.fixture
def registered_user(
    api_client: ApiClient,
    user_data: dict[str, str],
    cleanup_user: Callable[[str], None],
) -> dict[str, Any]:
    data = register_user(api_client, user_data)
    cleanup_user(data["accessToken"])
    return data


@pytest.fixture
def ingredients(api_client: ApiClient) -> list[dict[str, Any]]:
    return get_ingredients(api_client)
