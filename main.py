from typing import Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.utils import deep_update

from cache import CachedValue

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


class TodoItem(BaseModel):
  task: str
  completed: bool
  timestamp: str

todos = CachedValue('todos')

@app.get("/todos")
def get_todos():
    return todos.read()

@app.put('/add/{todo_id}', response_model=TodoItem)
def add_todo(todo_id: str, new_todo: TodoItem):
  
  def saver(existing):
    # raise Exception('intentional bug')
    return deep_update(existing, jsonable_encoder({ todo_id: new_todo }))
    # return jsonable_encoder({ todo_id: new_todo })
  
  todos.save(saver)

  return new_todo