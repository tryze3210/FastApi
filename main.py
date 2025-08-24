from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models
import schemas
from database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(title="Кулинарная книга API", lifespan=lifespan)


@app.post("/recipes", response_model=schemas.RecipeDetail, summary="Создать рецепт")
async def create_recipe(
    recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)
):
    db_recipe = await crud.create_recipe(db, recipe)

    return schemas.RecipeDetail(
        id=db_recipe.id,
        title=db_recipe.title,
        cooking_time=db_recipe.cooking_time,
        views=db_recipe.views,
        ingredients=db_recipe.ingredients.split(","),
        description=db_recipe.description,
    )


@app.get("/recipes", response_model=List[schemas.RecipeRead], summary="Список рецептов")
async def read_recipes(db: AsyncSession = Depends(get_db)):
    return await crud.get_recipes(db)


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetail,
    summary="Детали рецепта",
)
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return schemas.RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        views=recipe.views,
        ingredients=recipe.ingredients.split(","),
        description=recipe.description,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
