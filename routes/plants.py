from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.utils import deep_update
from cache import CachedValue
from pydantic import BaseModel, RootModel
from typing import Dict, Optional

from datetime import datetime, timedelta
from util import get_now

class Plant(BaseModel):
  name: str
  iconName: str
  purchaseDate: str
  waterFrequency: int
  lightConditions: str
  waterHistory: list[str]
  delayUntil: str
PlantList = RootModel[Dict[str, Plant]]

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
    newPlantWithHistory = Plant(
      name=plant.name,
      iconName=plant.iconName,
      purchaseDate=plant.purchaseDate,
      waterFrequency=plant.waterFrequency,
      lightConditions=plant.lightConditions,
      waterHistory=plant.waterHistory,
      delayUntil=plant.delayUntil
    )
    return deep_update(existing_plants, jsonable_encoder({ plant_id: newPlantWithHistory }))

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

@router.post('/water/{plant_id}')
def water_plant(plant_id: str, water_event: WaterEvent):
  date = water_event.date
  def internal_water_plant(existing_plants: PlantList):
    if plant_id not in existing_plants:
      raise HTTPException(status_code=404, detail=f'Plant ID: {plant_id} could not be found to water')
    stored_plant = existing_plants[plant_id]
    if 'waterHistory' not in stored_plant:
      stored_plant['waterHistory'] = []
    stored_plant_model = Plant(**stored_plant)
    if date not in stored_plant_model.waterHistory:
      stored_plant_model.waterHistory.append(date)
    else:
      # Already watered on this day, so delete it to make un-watering available incase used by mistake
      stored_plant_model.waterHistory.remove(date)
    return deep_update(existing_plants, jsonable_encoder({ plant_id: stored_plant_model }))

  plants.save(internal_water_plant)

@router.post('/delay/{plant_id}')
def delay_plant_water(plant_id: str, delay_event: DelayEvent):
  days = delay_event.days

  def internal_delay_plant_water(existing_plants: PlantList):
    if plant_id not in existing_plants:
      raise HTTPException(status_code=404, detail=f'Plant ID: {plant_id} could not be found to delay')
    stored_plant = existing_plants[plant_id]
    if 'delayUntil' not in stored_plant:
      stored_plant['delayUntil'] = ''
    stored_plant_model = Plant(**stored_plant)

    def is_in_past(date: str) -> bool:
      date_obj = datetime.strptime(date, "%Y-%m-%d").date()
      return date_obj < get_now().date()
    
    date_reference_point = get_now() if len(stored_plant_model.delayUntil) == 0 or is_in_past(stored_plant_model.delayUntil) else datetime.strptime(stored_plant_model.delayUntil, "%Y-%m-%d")

    new_delay_date = date_reference_point + timedelta(days=days)    
    stored_plant_model.delayUntil = new_delay_date.strftime("%Y-%m-%d")
    return deep_update(existing_plants, jsonable_encoder({ plant_id: stored_plant_model }))

  plants.save(internal_delay_plant_water)
