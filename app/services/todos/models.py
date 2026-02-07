from typing import Optional
from pydantic import BaseModel


class TodoItem(BaseModel):
  task: str
  completed: bool
  timestamp: str
  creator_id: str
  description: Optional[str] = None
  assignee_id: Optional[str] = None
  deadline: Optional[str] = None

class PartialTodoItem(TodoItem):
  task: Optional[str] = None
  completed: Optional[bool] = None
  timestamp: Optional[str] = None
  creator_id: Optional[str] = None
