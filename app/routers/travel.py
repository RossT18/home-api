from app.services.travel.main import get_directions_response, format_bus_directions_response
from app.services.travel.models import BusInfo
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from typing import List


router = APIRouter(
  prefix='/travel',
  tags=['travel']
)

@router.get('/bus', response_model=List[BusInfo])
def get_bus_journey_info() -> List[BusInfo]:
  bus_directions_response = get_directions_response('bus')
  formatted = format_bus_directions_response(bus_directions_response)
  return jsonable_encoder(formatted)
