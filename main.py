from contextlib import asynccontextmanager
from typing import AsyncGenerator, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Кулинарная книга API", lifespan=lifespan)


@app.post("/recipes", response_model=schemas.RecipeDetail)
async def create_recipe(
    recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)
) -> schemas.RecipeDetail:
    db_recipe = await crud.create_recipe(db, recipe)
    return schemas.RecipeDetail.from_orm(db_recipe)


@app.get("/recipes", response_model=List[schemas.RecipeRead])
async def read_recipes(db: AsyncSession = Depends(get_db)) -> List[schemas.RecipeRead]:
    recipes = await crud.get_recipes(db)
    return [schemas.RecipeRead.from_orm(r) for r in recipes]


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
async def read_recipe(
    recipe_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.RecipeDetail:
    recipe = await crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return schemas.RecipeDetail.from_orm(recipe)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
