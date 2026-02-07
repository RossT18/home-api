from app.services.todos.models import TodoItem, PartialTodoItem
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.utils import deep_update
from typing import Dict
from app.cache import CachedValue

router = APIRouter(
  prefix='/todos',
  tags=['todos']
)

todos = CachedValue('todos')

@router.get('/', response_model=Dict[str, TodoItem])
def get_todos() -> Dict[str, TodoItem]:
  return jsonable_encoder(todos.read())

@router.put('/add/{todo_id}', status_code=201)
def add_todo(todo_id: str, new_todo: TodoItem):
  def add_new_todo(existing_todos):
    if todo_id in existing_todos:
      raise HTTPException(status_code=409, detail=f'Todo ID: {todo_id} already exists')
    return deep_update(existing_todos, jsonable_encoder({ todo_id: new_todo }))

  todos.save(add_new_todo)

@router.patch('/update/{todo_id}')
def update_todo(todo_id: str, todo: PartialTodoItem):
  def edit_todo(existing_todos):
    if todo_id not in existing_todos:
      raise HTTPException(status_code=404, detail=f'Todo ID: {todo_id} could not be found to update')
    stored_todo_model = TodoItem(**existing_todos[todo_id])
    update_todo_data = todo.model_dump(exclude_unset=True)
    updated_todo = stored_todo_model.model_copy(update=update_todo_data)
    return deep_update(existing_todos, jsonable_encoder({ todo_id: updated_todo }))

  todos.save(edit_todo)

@router.delete('/delete/{todo_id}', status_code=204)
def delete_todo(todo_id: str):
  def del_todo(existing_todos):
    if todo_id not in existing_todos:
      raise HTTPException(status_code=404, detail=f'Todo ID: {todo_id} could not be found to delete')
    del existing_todos[todo_id]
    return jsonable_encoder(existing_todos)

  todos.save(del_todo)
