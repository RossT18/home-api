from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, RootModel
from pydantic.utils import deep_update
from typing import Dict, Optional
from cache import CachedValue

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

router = APIRouter(
  prefix='/meals',
  tags=['meals']
)

meal_plan = CachedValue('meal_plan')
meal_archive = CachedValue('meal_archive')

@router.get('/plan', response_model=MealPlan)
def get_meal_plan() -> MealPlan:
  return jsonable_encoder(meal_plan.read())

@router.put('/add/{meal_id}', status_code=201)
def add_meal(meal_id: str, meal: Meal):
  def add_to_plan(existing_plan):
    if meal_id in existing_plan:
      raise HTTPException(status_code=409, detail=f'Meal ID: {meal_id} already exists')
    return deep_update(existing_plan, jsonable_encoder({ meal_id: meal }))

  meal_plan.save(add_to_plan)

@router.patch('/update/{meal_id}')
def edit_meal(meal_id: str, meal: PartialMeal):
  def edit_plan(existing_plan):
    if meal_id not in existing_plan:
      raise HTTPException(status_code=404, detail=f'Meal ID: {meal_id} could not be found to update')
    stored_meal_model = Meal(**existing_plan[meal_id])
    update_meal_data = meal.model_dump(exclude_unset=True)
    updated_meal = stored_meal_model.model_copy(update=update_meal_data)
    return deep_update(existing_plan, jsonable_encoder({ meal_id: updated_meal }))
  
  meal_plan.save(edit_plan)

@router.delete('/delete/{meal_id}', status_code=204)
def delete_meal(meal_id: str):
  def del_meal(existing_plan):
    if meal_id not in existing_plan:
      raise HTTPException(status_code=404, detail=f'Meal ID: {meal_id} could not be found to delete')
    del existing_plan[meal_id]
    return jsonable_encoder(existing_plan)

  meal_plan.save(del_meal)

@router.get('/archive', response_model=Archive)
def get_archive() -> Archive:
  return jsonable_encoder(meal_archive.read())

@router.put('/archive/add/{archive_id}', status_code=201)
def add_meals_to_archive(archive_id: str, archive: ArchiveEntry):
  def add_to_archive(existing_archive):
    if archive_id in existing_archive:
      raise HTTPException(status_code=409, detail=f'Archive ID: {archive_id} already exists')
    return deep_update(existing_archive, jsonable_encoder({ archive_id: archive }))

  meal_archive.save(add_to_archive)

@router.delete('/archive/delete/{archive_id}', status_code=204)
def delete_archive(archive_id: str):
  def del_archive(existing_archive):
    if archive_id not in existing_archive:
      raise HTTPException(status_code=404, detail=f'Archive ID: {archive_id} could not be found to delete')
    del existing_archive[archive_id]
    return jsonable_encoder(existing_archive)

  meal_archive.save(del_archive)
