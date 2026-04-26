from typing import Optional
from pydantic import BaseModel


class Meal(BaseModel):
    # id is optional for input (created by the DB) but present on stored rows
    id: Optional[int] = None
    name: str
    date: str
    mealTime: str


class PartialMeal(Meal):
    name: Optional[str] = None
    date: Optional[str] = None
    mealTime: Optional[str] = None
