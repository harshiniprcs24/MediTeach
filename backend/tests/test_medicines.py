import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def get_auth_token(client: AsyncClient) -> str:
    payload = {
        "name": "Med User",
        "email": "meduser@example.com",
        "password": "Test1234",
        "preferred_language": "en",
    }
    r = await client.post("/api/v1/auth/register", json=payload)
    if r.status_code == 409:
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": payload["email"], "password": payload["password"]},
        )
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_search_medicines_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_auth_token(client)
        response = await client.get(
            "/api/v1/medicines/search?q=paracetamol",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_search_medicines_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/medicines/search?q=aspirin")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_medicine_by_id_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_auth_token(client)
        response = await client.get(
            "/api/v1/medicines/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_interactions_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_auth_token(client)
        response = await client.post(
            "/api/v1/medicines/interactions",
            json={"medicine_ids": []},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert "interactions" in response.json()
