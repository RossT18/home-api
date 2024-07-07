from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
  prefix='/weather',
  tags=['weather']
)

class Weather(BaseModel):
  sunrise: str
  sunset: str
  temp: int
  weather: str
  description: str
  icon: str

def get_weather_response():
  api_key = os.getenv('OPENWEATHERMAP_API_KEY')
  lat = os.getenv('LAT')
  lon = os.getenv('LON')
  if api_key is None or lat is None or lon is None:
    raise HTTPException(status_code=500, detail=f'Secret weather data could not be loaded ({"API_KEY" if api_key is None else "LOCATION"})')
  url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
  headers = {'Content-type': 'application/json'}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
     raise HTTPException(status_code=r.status_code, detail=f'Error retrieving weather information. Reason: {r.reason}')
  return r.json()

def format_weather_response(data) -> Weather:
  def format_time(timestamp):
    return datetime.fromtimestamp(timestamp, ZoneInfo('Europe/London')).strftime("%H:%M")
  current = data['current']
  return Weather(
    sunrise=format_time(current['sunrise']),
    sunset=format_time(current['sunset']),
    temp=int(round(current['temp'])),
    weather=current['weather'][0]['main'],
    description=current['weather'][0]['description'],
    icon=current['weather'][0]['icon']
  )

@router.get('/', response_model=Weather)
def get_weather() -> Weather:
  weather_response = get_weather_response()
  formatted = format_weather_response(weather_response)
  return jsonable_encoder(formatted)
