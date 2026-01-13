from app.services.weather.main import get_weather_response, format_weather_response
from app.services.weather.models import Weather
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder


router = APIRouter(
  prefix='/weather',
  tags=['weather']
)

@router.get('/', response_model=Weather)
def get_weather() -> Weather:
  weather_response = get_weather_response()
  formatted = format_weather_response(weather_response)
  return jsonable_encoder(formatted)
