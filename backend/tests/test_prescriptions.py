import pytest
import io
from httpx import AsyncClient, ASGITransport
from app.main import app

# ── helpers ──────────────────────────────────────────────────────────────────

async def get_auth_token(client: AsyncClient) -> str:
    payload = {
        "name": "Presc User",
        "email": "prescuser@example.com",
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


def make_image_file(filename: str = "test.jpg") -> tuple:
    """Create a minimal JPEG-like bytes object for upload testing."""
    content = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # minimal JPEG header
    return ("file", (filename, io.BytesIO(content), "image/jpeg"))


# ── tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_prescriptions_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_auth_token(client)
        response = await client.get(
            "/api/v1/prescriptions",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_prescription_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_auth_token(client)
        response = await client.get(
            "/api/v1/prescriptions/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_prescription_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_auth_token(client)
        response = await client.delete(
            "/api/v1/prescriptions/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_prescriptions_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/prescriptions")
    assert response.status_code == 403
