from typing import Any

import allure
import pytest

from tests.api_client import ApiClient


@allure.feature("Изменение данных пользователя")
class TestUserProfile:
    @allure.title("Авторизованный пользователь изменяет поле {field}")
    @pytest.mark.parametrize("field", ["name", "email"])
    def test_update_user_data_with_authorization(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
        field: str,
    ) -> None:
        user = registered_user["payload"]
        new_value = (
            f"updated-{user['email']}" if field == "email" else f"Updated {user['name']}"
        )
        with allure.step(f"Изменить поле {field} с accessToken"):
            response = api_client.request(
                "PATCH",
                "/auth/user",
                payload={field: new_value},
                token=registered_user["accessToken"],
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["user"][field] == new_value
        other_field = "name" if field == "email" else "email"
        assert body["user"][other_field] == user[other_field]

    @allure.title("Изменение поля {field} без авторизации запрещено")
    @pytest.mark.parametrize("field", ["name", "email"])
    def test_update_user_data_without_authorization(
        self,
        api_client: ApiClient,
        user_data: dict[str, str],
        field: str,
    ) -> None:
        payload = {
            field: f"unauthorized-{user_data[field]}" if field == "email"
            else f"Unauthorized {user_data[field]}"
        }
        with allure.step(f"Попытаться изменить поле {field} без токена"):
            response = api_client.request("PATCH", "/auth/user", payload=payload)

        assert response.status_code == 401
        assert response.json() == {
            "success": False,
            "message": "You should be authorised",
        }
