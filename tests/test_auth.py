from typing import Any

import allure
import pytest

from tests.api_client import ApiClient
from tests.constants import LOGIN, REGISTER
from tests.helpers import missing_field_payload


@allure.feature("Регистрация и авторизация")
class TestUserRegistration:
    @allure.title("Успешная регистрация нового пользователя")
    def test_register_new_user(
        self,
        api_client: ApiClient,
        user_data: dict[str, str],
        cleanup_user: Any,
    ) -> None:
        with allure.step("Отправить данные нового пользователя"):
            response = api_client.request("POST", REGISTER, payload=user_data)

        assert response.status_code == 200
        body = response.json()
        cleanup_user(body["accessToken"])
        assert body["success"] is True
        assert body["user"] == {
            "email": user_data["email"],
            "name": user_data["name"],
        }
        assert body.get("accessToken")
        assert body.get("refreshToken")

    @allure.title("Повторная регистрация существующего пользователя запрещена")
    def test_register_existing_user(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
    ) -> None:
        with allure.step("Повторно отправить данные зарегистрированного пользователя"):
            response = api_client.request(
                "POST", REGISTER, payload=registered_user["payload"]
            )

        assert response.status_code == 403
        assert response.json() == {
            "success": False,
            "message": "User already exists",
        }

    @allure.title("Регистрация без обязательного поля {field} отклоняется")
    @pytest.mark.parametrize("field", ["email", "password", "name"])
    def test_register_without_required_field(
        self,
        api_client: ApiClient,
        user_data: dict[str, str],
        field: str,
    ) -> None:
        payload = missing_field_payload(user_data, field)
        with allure.step(f"Отправить данные без поля {field}"):
            response = api_client.request("POST", REGISTER, payload=payload)

        assert response.status_code == 403
        assert response.json() == {
            "success": False,
            "message": "Email, password and name are required fields",
        }


@allure.feature("Регистрация и авторизация")
class TestUserLogin:
    @allure.title("Успешный вход с правильными данными")
    def test_login_with_correct_credentials(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
    ) -> None:
        payload = registered_user["payload"]
        with allure.step("Войти с зарегистрированными данными"):
            response = api_client.request(
                "POST",
                LOGIN,
                payload={"email": payload["email"], "password": payload["password"]},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["user"] == {
            "email": payload["email"],
            "name": payload["name"],
        }
        assert body.get("accessToken")
        assert body.get("refreshToken")

    @allure.title("Вход с некорректным {credential} отклоняется")
    @pytest.mark.parametrize(
        ("credential", "value"),
        [("email", "missing-user@example.com"), ("password", "WrongPassword!")],
    )
    def test_login_with_incorrect_credentials(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
        credential: str,
        value: str,
    ) -> None:
        payload = registered_user["payload"]
        login_data = {"email": payload["email"], "password": payload["password"]}
        login_data[credential] = value
        with allure.step(f"Войти с некорректным значением {credential}"):
            response = api_client.request("POST", LOGIN, payload=login_data)

        assert response.status_code == 401
        assert response.json() == {
            "success": False,
            "message": "email or password are incorrect",
        }
