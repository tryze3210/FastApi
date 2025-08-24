from typing import AsyncGenerator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from database import Base, engine
from main import app


@pytest_asyncio.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)

    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.mark.asyncio
async def test_create_read_recipe(async_client: AsyncClient) -> None:
    new_recipe = {
        "title": "Омлет",
        "cooking_time": 10,
        "ingredients": ["Яйца", "Молоко", "Соль"],
        "description": "Быстрый и вкусный омлет.",
    }

    response = await async_client.post("/recipes", json=new_recipe)
    assert response.status_code == 200
    created = response.json()
    assert created["title"] == new_recipe["title"]
