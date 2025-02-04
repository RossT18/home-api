from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.utils import deep_update
from cache import CachedValue
from pydantic import BaseModel, RootModel
from typing import Dict, Optional

class Plant(BaseModel):
  name: str
  iconName: str
  purchaseDate: str
  waterFrequency: int
  lightConditions: str
PlantList = RootModel[Dict[str, Plant]]

class PartialPlant(Plant):
  name: Optional[str] = None
  iconName: Optional[str] = None
  purchaseDate: Optional[str] = None
  waterFrequency: Optional[int] = None
  lightConditions: Optional[str] = None

router = APIRouter(
  prefix='/plants',
  tags=['plants']
)

plants = CachedValue('plants')


@router.get('/', response_model=PlantList)
def get_plants():
  return jsonable_encoder(plants.read())

@router.get('/plant/{plant_id}', response_model=Plant)
def get_plant(plant_id: str):
  existing_plants = plants.read()
  if plant_id not in existing_plants:
    raise HTTPException(status_code=404, detail=f'Plant ID: {plant_id} could not be found to get')
  
  return jsonable_encoder(existing_plants[plant_id])

@router.put('/add/{plant_id}', status_code=201)
def add_plant(plant_id: str, plant: Plant):
  def add_to_plants(existing_plants):
    if plant_id in existing_plants:
      raise HTTPException(status_code=409, detail=f'Plant ID: {plant_id} already exists')
    return deep_update(existing_plants, jsonable_encoder({ plant_id: plant }))

  plants.save(add_to_plants)

@router.patch('/update/{plant_id}')
def edit_plant(plant_id: str, plant: PartialPlant):
  def edit_plants(existing_plants):
    if plant_id not in existing_plants:
      raise HTTPException(status_code=404, detail=f'Plant ID: {plant_id} could not be found to update')
    stored_plant_model = Plant(**existing_plants[plant_id])
    update_plant_data = plant.model_dump(exclude_unset=True)
    updated_plant = stored_plant_model.model_copy(update=update_plant_data)
    return deep_update(existing_plants, jsonable_encoder({ plant_id: updated_plant }))
  
  plants.save(edit_plants)

@router.delete('/delete/{plant_id}', status_code=204)
def delete_plant(plant_id: str):
  def del_plant(existing_plant):
    if plant_id not in existing_plant:
      raise HTTPException(status_code=404, detail=f'Plant ID: {plant_id} could not be found to delete')
    del existing_plant[plant_id]
    return jsonable_encoder(existing_plant)

  plants.save(del_plant)