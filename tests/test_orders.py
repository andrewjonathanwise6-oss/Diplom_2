from typing import Any

import allure

from tests.api_client import ApiClient
from tests.constants import ORDERS
from tests.helpers import create_order_for_user, ingredient_ids


@allure.feature("Создание заказа")
class TestCreateOrder:
    @allure.title("Создание заказа с ингредиентами и авторизацией")
    def test_create_order_with_authorization(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
        ingredients: list[dict[str, Any]],
    ) -> None:
        ids = ingredient_ids(ingredients)

        with allure.step("Создать заказ авторизованного пользователя"):
            response = api_client.request(
                "POST", ORDERS, payload={"ingredients": ids},
                token=registered_user["accessToken"],
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body.get("name")
        assert body["order"].get("number")
        assert body["order"].get("_id")
        assert [item["_id"] for item in body["order"]["ingredients"]] == ids

    @allure.title("Создание заказа с ингредиентами без авторизации")
    def test_create_order_without_authorization(
        self, api_client: ApiClient, ingredients: list[dict[str, Any]]
    ) -> None:
        with allure.step("Создать заказ без токена"):
            response = api_client.request(
                "POST", ORDERS, payload={"ingredients": ingredient_ids(ingredients)}
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body.get("name")
        assert body["order"].get("number")

    @allure.title("Создание заказа без ингредиентов отклоняется")
    def test_create_order_without_ingredients(
        self,
        api_client: ApiClient,
        registered_user: dict[str, Any],
    ) -> None:
        with allure.step("Отправить пустой список ингредиентов"):
            response = api_client.request(
                "POST",
                ORDERS,
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
                ORDERS,
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
                ORDERS,
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
        created_order_id = create_order_for_user(
            api_client, registered_user["accessToken"], ingredients
        )

        with allure.step("Запросить ленту заказов с accessToken"):
            response = api_client.request(
                "GET", ORDERS, token=registered_user["accessToken"]
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
            response = api_client.request("GET", ORDERS)

        assert response.status_code == 401
        assert response.json() == {
            "success": False,
            "message": "You should be authorised",
        }
