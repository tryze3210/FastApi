from pydantic import BaseModel, Field, ConfigDict
from typing import List

class RecipeCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Борщ"})
    cooking_time: int = Field(..., json_schema_extra={"example": 90}) 
    ingredients: List[str] = Field(..., json_schema_extra={"example": ["Вода", "Свекла", "Капуста", "Мясо"]})
    description: str = Field(..., json_schema_extra={"example": "Очень вкусный борщ"})

class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    cooking_time: int
    views: int

class RecipeDetail(RecipeRead):
    ingredients: List[str]
    description: str