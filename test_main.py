import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from database import Base, engine
from main import app


@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_create_read_recipe(async_client):
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
    assert created["cooking_time"] == new_recipe["cooking_time"]
    assert created["ingredients"] == new_recipe["ingredients"]
    assert created["description"] == new_recipe["description"]
    assert created["views"] == 0

    recipe_id = created["id"]

    response = await async_client.get("/recipes")
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 1
    assert recipes[0]["title"] == "Омлет"
    assert recipes[0]["views"] == 0

    response = await async_client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    detailed = response.json()
    assert detailed["id"] == recipe_id
    assert detailed["views"] == 1
    assert detailed["ingredients"] == new_recipe["ingredients"]

    response = await async_client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    detailed = response.json()
    assert detailed["views"] == 2
