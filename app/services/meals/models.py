from typing import Dict, Optional
from pydantic import BaseModel, RootModel


class Meal(BaseModel):
  name: str
  date: str
  mealTime: str

MealPlan = RootModel[Dict[str, Meal]]

class PartialMeal(Meal):
  name: Optional[str] = None
  date: Optional[str] = None
  mealTime: Optional[str] = None

class ArchiveEntry(BaseModel):
  minDate: str
  maxDate: str
  mealPlan: MealPlan

Archive = RootModel[Dict[str, ArchiveEntry]]