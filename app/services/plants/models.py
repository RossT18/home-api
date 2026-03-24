from typing import Optional
from pydantic import BaseModel


class Plant(BaseModel):
  id: Optional[int] = None
  name: str
  iconName: str
  purchaseDate: str
  waterFrequency: int
  lightConditions: str
  waterHistory: list[str]
  delayUntil: Optional[str] = None

class PartialPlant(BaseModel):
  name: Optional[str] = None
  iconName: Optional[str] = None
  purchaseDate: Optional[str] = None
  waterFrequency: Optional[int] = None
  lightConditions: Optional[str] = None
  waterHistory: Optional[list[str]] = None
  delayUntil: Optional[str] = None

class WaterEvent(BaseModel):
  date: str

class DelayEvent(BaseModel):
  days: int
  """Number of days to delay the watering"""
  date: str
  """Date to delay the watering from in ISO format"""
