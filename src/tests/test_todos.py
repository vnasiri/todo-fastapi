import pytest
from httpx import AsyncClient
from starlette import status

from src.tests.example import VALID_TODO, VALID_TODO_UPDATE

BASE_URL = "/api/v1/todos/"


@pytest.mark.asyncio
class TestTodoAPI:
    """Grouped tests for better organization and shared markers."""

    async def test_unauthorized_access(self, client: AsyncClient):
        """Security: Verify no-token access is blocked."""
        response = await client.post(BASE_URL, json=VALID_TODO)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_todo_invalid_data(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Input Validation: Verify 422 for bad schemas."""
        response = await client.post(
            BASE_URL,
            json={"title": ""},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_create_and_read_todo(self, client: AsyncClient, auth_headers: dict):
        """Happy Path: Standard CRUD flow."""
        # Create
        create_res = await client.post(BASE_URL, json=VALID_TODO, headers=auth_headers)
        assert create_res.status_code == status.HTTP_201_CREATED
        todo_id = create_res.json()["id"]

        # Read
        get_res = await client.get(f"{BASE_URL}/{todo_id}", headers=auth_headers)
        assert get_res.status_code == status.HTTP_200_OK
        assert get_res.json()["title"] == VALID_TODO["title"]

    async def test_update_todo_persists(self, client: AsyncClient, auth_headers: dict):
        """Data Integrity: Ensure updates are actually saved."""
        res = await client.post(BASE_URL, json=VALID_TODO, headers=auth_headers)
        todo_id = res.json()["id"]

        update_res = await client.put(
            f"{BASE_URL}/{todo_id}", json=VALID_TODO_UPDATE, headers=auth_headers
        )
        assert update_res.status_code == status.HTTP_200_OK
        assert update_res.json()["is_completed"] is True

    async def test_delete_todo(self, client: AsyncClient, auth_headers: dict):
        """Lifecycle: Ensure resource is removed from the system."""
        res = await client.post(BASE_URL, json=VALID_TODO, headers=auth_headers)
        todo_id = res.json()["id"]

        await client.delete(f"{BASE_URL}/{todo_id}", headers=auth_headers)
        check = await client.get(f"{BASE_URL}{todo_id}", headers=auth_headers)
        assert check.status_code == status.HTTP_404_NOT_FOUND
