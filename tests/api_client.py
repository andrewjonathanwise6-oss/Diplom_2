from typing import Any

import requests


BASE_URL = "https://qa-stellarburgers.education-services.ru/api"


class ApiClient:
    def __init__(self) -> None:
        self.session = requests.Session()

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        payload: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> requests.Response:
        headers = {"Authorization": token} if token else None
        return self.session.request(
            method,
            f"{BASE_URL}{endpoint}",
            json=payload,
            headers=headers,
            timeout=15,
        )

    def close(self) -> None:
        self.session.close()
