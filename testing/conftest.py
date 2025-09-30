import pytest
import requests


BASE_URL = "http://localhost:8000/graphql"


@pytest.fixture(scope="session")
def graphql_client():
    def _post(query: str, variables: dict = None, headers: dict = None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(BASE_URL, json=payload, headers=headers or {})
        response.raise_for_status()
        return response.json()

    return _post
