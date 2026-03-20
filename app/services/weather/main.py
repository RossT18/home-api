from app.services.shared.models import Point
from app.services.weather.models import WeatherType, Weather
from fastapi import HTTPException
import requests
from datetime import datetime
from zoneinfo import ZoneInfo


def get_weather_type_from_code(code: int) -> WeatherType:
  def get_icon_url(icon_name):
    valid_icons = ['01d', '02d', '03d', '04d', '09d', '10d', '11d', '13d', '50d']
    if icon_name not in valid_icons:
      # Return clear sky by default
      print(f'Error getting weather icon with name {icon_name}')
      return "http://openweathermap.org/img/wn/01d@2x.png"
    return f"http://openweathermap.org/img/wn/{icon_name}@2x.png"

  codes: dict[int, WeatherType] = {
    0: WeatherType(name='Clear sky', icon=get_icon_url('01d')),
    1: WeatherType(name='Mainly clear', icon=get_icon_url('01d')),
    2: WeatherType(name='Partly cloudy', icon=get_icon_url('02d')),
    3: WeatherType(name='Overcast', icon=get_icon_url('03d')),
    45: WeatherType(name='Fog', icon=get_icon_url('50d')),
    48: WeatherType(name='Fog', icon=get_icon_url('50d')),
    51: WeatherType(name='Light drizzle', icon=get_icon_url('10d')),
    53: WeatherType(name='Drizzle', icon=get_icon_url('10d')),
    55: WeatherType(name='Heavy drizzle', icon=get_icon_url('10d')),
    56: WeatherType(name='Light freezing drizzle', icon=get_icon_url('10d')),
    57: WeatherType(name='Heavy freezing drizzle', icon=get_icon_url('10d')),
    61: WeatherType(name='Light rain', icon=get_icon_url('10d')),
    63: WeatherType(name='Rain', icon=get_icon_url('10d')),
    65: WeatherType(name='Heavy rain', icon=get_icon_url('09d')),
    66: WeatherType(name='Light freezing rain', icon=get_icon_url('13d')),
    67: WeatherType(name='Heavy freezing rain', icon=get_icon_url('13d')),
    71: WeatherType(name='Light snow', icon=get_icon_url('13d')),
    73: WeatherType(name='Snow', icon=get_icon_url('13d')),
    75: WeatherType(name='Heavy snow', icon=get_icon_url('13d')),
    77: WeatherType(name='Snow grains', icon=get_icon_url('13d')),
    80: WeatherType(name='Light rain showers', icon=get_icon_url('09d')),
    81: WeatherType(name='Rain showers', icon=get_icon_url('09d')),
    82: WeatherType(name='Heavy rain showers', icon=get_icon_url('09d')),
    85: WeatherType(name='Light snow showers', icon=get_icon_url('13d')),
    86: WeatherType(name='Heavy snow showers', icon=get_icon_url('13d')),
    95: WeatherType(name='Thunderstorms', icon=get_icon_url('11d')),
    96: WeatherType(name='Thunderstorms and hail', icon=get_icon_url('11d')),
    99: WeatherType(name='Thunderstorms and heavy hail', icon=get_icon_url('11d'))
  }
  return codes[code] if code in codes else WeatherType(name='Weather Unavailable', icon=get_icon_url(''))

def get_weather_response(location: Point):
  open_meteo_api_params = {
    "latitude": str(location.latitude),
    "longitude": str(location.longitude),
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
    weather=weather_type.name,
    icon=weather_type.icon
  )
