from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Recipe
from schemas import RecipeCreate


async def create_recipe(db: AsyncSession, recipe: RecipeCreate):
    db_recipe = Recipe(
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        ingredients=",".join(recipe.ingredients),
        description=recipe.description,
    )
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe


async def get_recipes(db: AsyncSession):
    result = await db.execute(
        select(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time.asc())
    )
    return result.scalars().all()


async def get_recipe_by_id(db: AsyncSession, recipe_id: int):
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if recipe:
        recipe.views += 1
        await db.commit()
        await db.refresh(recipe)
    return recipe
