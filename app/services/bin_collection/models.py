from typing import List
from pydantic import BaseModel


class Collection(BaseModel):
  date: str
  bins: List[str]

class BinSchedule(BaseModel):
  collections: List[Collection]
  next: Collection
