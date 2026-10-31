from typing import Any

import allure
import pytest

from tests.api_client import ApiClient


@allure.feature("Создание заказа")
class TestCreateOrder:
    @allure.title("Создание заказа с ингредиентами, авторизация: {with_authorization}")
    @pytest.mark.parametrize("with_authorization", [True, False])
    def test_create_order_with_ingredients(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
        ingredients: list[dict[str, Any]],
        with_authorization: bool,
    ) -> None:
        bun = next(item for item in ingredients if item["type"] == "bun")
        filling = next(item for item in ingredients if item["type"] != "bun")
        ingredient_ids = [bun["_id"], filling["_id"]]
        token = registered_user["accessToken"] if with_authorization else None

        with allure.step("Создать заказ с актуальными ID из API ингредиентов"):
            response = api_client.request(
                "POST",
                "/orders",
                payload={"ingredients": ingredient_ids},
                token=token,
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body.get("name")
        order = body["order"]
        assert order.get("number")
        if with_authorization:
            assert order.get("_id")
            assert [item["_id"] for item in order["ingredients"]] == ingredient_ids

    @allure.title("Создание заказа без ингредиентов отклоняется")
    def test_create_order_without_ingredients(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
    ) -> None:
        with allure.step("Отправить пустой список ингредиентов"):
            response = api_client.request(
                "POST",
                "/orders",
                payload={"ingredients": []},
                token=registered_user["accessToken"],
            )

        assert response.status_code == 400
        assert response.json() == {
            "success": False,
            "message": "Ingredient ids must be provided",
        }

    @allure.title("Некорректный хеш ингредиента возвращает HTTP 500")
    def test_create_order_with_invalid_ingredient_hash(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
    ) -> None:
        with allure.step("Создать заказ с документированным невалидным хешем"):
            response = api_client.request(
                "POST",
                "/orders",
                payload={"ingredients": ["invalid-ingredient-hash"]},
                token=registered_user["accessToken"],
            )

        assert response.status_code == 500, response.text

    @allure.title("Некоторые неизвестные ID ингредиентов возвращают HTTP 400")
    @pytest.mark.parametrize(
        "invalid_hash",
        [
            "invalid-hash",
            "000000000000000000000000",
        ],
        ids=["malformed-short", "unknown-object-id"],
    )
    def test_create_order_with_unknown_ingredient_id_returns_bad_request(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
        invalid_hash: str,
    ) -> None:
        with allure.step("Отправить заведомо некорректный ID ингредиента"):
            response = api_client.request(
                "POST",
                "/orders",
                payload={"ingredients": [invalid_hash]},
                token=registered_user["accessToken"],
            )

        assert response.status_code == 400, response.text
        assert response.json() == {
            "success": False,
            "message": "One or more ids provided are incorrect",
        }


@allure.feature("Заказы пользователя")
class TestUserOrders:
    @allure.title("Авторизованный пользователь получает свои заказы")
    def test_get_user_orders_with_authorization(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
        ingredients: list[dict[str, Any]],
    ) -> None:
        bun = next(item for item in ingredients if item["type"] == "bun")
        filling = next(item for item in ingredients if item["type"] != "bun")
        with allure.step("Создать заказ для тестового пользователя"):
            created = api_client.request(
                "POST",
                "/orders",
                payload={"ingredients": [bun["_id"], filling["_id"]]},
                token=registered_user["accessToken"],
            )
        assert created.status_code == 200, created.text
        created_order_id = created.json()["order"]["_id"]

        with allure.step("Запросить ленту заказов с accessToken"):
            response = api_client.request(
                "GET", "/orders", token=registered_user["accessToken"]
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body.get("orders"), list)
        assert any(order["_id"] == created_order_id for order in body["orders"])
        assert isinstance(body.get("total"), int)
        assert isinstance(body.get("totalToday"), int)

    @allure.title("Получение заказов пользователя без авторизации запрещено")
    def test_get_user_orders_without_authorization(self, api_client: ApiClient) -> None:
        with allure.step("Запросить заказы без accessToken"):
            response = api_client.request("GET", "/orders")

        assert response.status_code == 401
        assert response.json() == {
            "success": False,
            "message": "You should be authorised",
        }
