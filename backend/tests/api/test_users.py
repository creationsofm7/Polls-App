
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_user(client: AsyncClient):
    response = await client.post("/api/users/", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
