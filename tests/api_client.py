from typing import Any

import requests

from tests.constants import BASE_URL


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
