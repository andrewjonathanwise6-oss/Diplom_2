from uuid import uuid4

from tests.constants import INGREDIENTS, ORDERS, REGISTER, USER


def new_user_data():
    unique = uuid4().hex
    return {
        "email": f"diplom-{unique}@example.com",
        "password": f"Pass-{unique}!",
        "name": f"Diplom User {unique[:8]}",
    }


def register_user(client, payload):
    response = client.request("POST", REGISTER, payload=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Не удалось подготовить пользователя: {response.status_code}")
    return {"payload": payload, **response.json()}


def delete_user(client, access_token):
    response = client.request("DELETE", USER, token=access_token)
    if response.status_code not in (200, 202):
        raise RuntimeError(f"Не удалось удалить тестового пользователя: {response.status_code}")


def get_ingredients(client):
    response = client.request("GET", INGREDIENTS)
    if response.status_code != 200:
        raise RuntimeError(f"Не удалось получить ингредиенты: {response.status_code}")
    data = response.json().get("data")
    if not data:
        raise RuntimeError("API вернул пустой список ингредиентов")
    return data


def ingredient_ids(ingredients):
    bun = next(item for item in ingredients if item["type"] == "bun")
    filling = next(item for item in ingredients if item["type"] != "bun")
    return [bun["_id"], filling["_id"]]


def create_order_for_user(client, token, ingredients):
    response = client.request("POST", ORDERS, payload={"ingredients": ingredient_ids(ingredients)}, token=token)
    if response.status_code != 200:
        raise RuntimeError(f"Не удалось подготовить заказ: {response.status_code}")
    return response.json()["order"]["_id"]


def missing_field_payload(data, field):
    return {key: value for key, value in data.items() if key != field}


def updated_field_value(field, value):
    return f"updated-{value}" if field == "email" else f"Updated {value}"


def unauthorized_field_value(field, value):
    return f"unauthorized-{value}" if field == "email" else f"Unauthorized {value}"
