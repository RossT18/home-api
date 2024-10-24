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
  temperature: int
  weather: str
  icon: str

class WeatherType:
  name: str
  icon: str

def get_weather_type_from_code(code: int) -> WeatherType:
  def get_icon_url(icon_name):
    valid_icons = ['01d', '02d', '03d', '04d', '09d', '10d', '11d', '13d', '50d']
    if icon_name not in valid_icons:
      # Return clear sky by default
      print(f'Error getting weather icon with name {icon_name}')
      return "http://openweathermap.org/img/wn/01d@2x.png"
    return f"http://openweathermap.org/img/wn/{icon_name}@2x.png"

  codes = {
    0: { 'name': 'Clear sky', 'icon': get_icon_url('01d') },
    1: { 'name': 'Mainly clear', 'icon': get_icon_url('01d') },
    2: { 'name': 'Partly cloudy', 'icon': get_icon_url('02d') },
    3: { 'name': 'Overcast', 'icon': get_icon_url('03d') },
    45: { 'name': 'Fog', 'icon': get_icon_url('50d') },
    48: { 'name': 'Fog', 'icon': get_icon_url('50d') },
    51: { 'name': 'Light drizzle', 'icon': get_icon_url('10d') },
    53: { 'name': 'Drizzle', 'icon': get_icon_url('10d') },
    55: { 'name': 'Heavy drizzle', 'icon': get_icon_url('10d') },
    56: { 'name': 'Light freezing drizzle', 'icon': get_icon_url('10d') },
    57: { 'name': 'Heavy freezing drizzle', 'icon': get_icon_url('10d') },
    61: { 'name': 'Light rain', 'icon': get_icon_url('10d') },
    63: { 'name': 'Rain', 'icon': get_icon_url('10d') },
    65: { 'name': 'Heavy rain', 'icon': get_icon_url('09d') },
    66: { 'name': 'Light freezing rain', 'icon': get_icon_url('13d') },
    67: { 'name': 'Heavy freezing rain', 'icon': get_icon_url('13d') },
    71: { 'name': 'Light snow', 'icon': get_icon_url('13d') },
    73: { 'name': 'Snow', 'icon': get_icon_url('13d') },
    75: { 'name': 'Heavy snow', 'icon': get_icon_url('13d') },
    77: { 'name': 'Snow grains', 'icon': get_icon_url('13d') },
    80: { 'name': 'Light rain showers', 'icon': get_icon_url('09d') },
    81: { 'name': 'Rain showers', 'icon': get_icon_url('09d') },
    82: { 'name': 'Heavy rain showers', 'icon': get_icon_url('09d') },
    85: { 'name': 'Light snow showers', 'icon': get_icon_url('13d') },
    86: { 'name': 'Heavy snow showers', 'icon': get_icon_url('13d') },
    95: { 'name': 'Thunderstorms', 'icon': get_icon_url('11d') },
    96: { 'name': 'Thunderstorms and hail', 'icon': get_icon_url('11d') },
    99: { 'name': 'Thunderstorms and heavy hail', 'icon': get_icon_url('11d') }
  }
  return codes[code] if code in codes else { 'name': 'Weather Unavailable', 'icon': get_icon_url('') }

def get_weather_response():
  lat = os.getenv('LAT')
  lon = os.getenv('LON')
  if lat is None or lon is None:
    raise HTTPException(status_code=500, detail=f'Secret weather data (LOCATION) could not be loaded')

  open_meteo_api_params = {
    "latitude": str(lat),
    "longitude": str(lon),
    "current": "temperature_2m,apparent_temperature,precipitation,weather_code",
    "hourly": "temperature_2m,apparent_temperature,precipitation,weather_code",
    "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
    "wind_speed_unit": "mph",
    "timezone": "Europe%2FLondon",
    "past_days": "1",
    "forecast_days": "3",
    "timeformat": "unixtime",
    "models": "ukmo_seamless"
  }
  url = 'https://api.open-meteo.com/v1/forecast?'

  for key, value in open_meteo_api_params.items():
    url += f"{key}={value}&"

  headers = {'Content-type': 'application/json'}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
     raise HTTPException(status_code=r.status_code, detail=f'Error retrieving weather information. Reason: {r.reason}')
  return r.json()

def format_weather_response(data) -> Weather:
  def format_time(timestamp):
    return datetime.fromtimestamp(timestamp, ZoneInfo(data['timezone'])).strftime("%H:%M")
  
  current = data['current']
  weather_type = get_weather_type_from_code(current['weather_code'])
  return Weather(
    sunrise=format_time(data['daily']['sunrise'][1]),
    sunset=format_time(data['daily']['sunset'][1]),
    temperature=int(round(current['temperature_2m'])),
    weather=weather_type['name'],
    icon=weather_type['icon']
  )

@router.get('/', response_model=Weather)
def get_weather() -> Weather:
  weather_response = get_weather_response()
  formatted = format_weather_response(weather_response)
  return jsonable_encoder(formatted)
