from enum import StrEnum
from pydantic import BaseModel


class Directions(BaseModel):
  duration: int
  """Duration of journey in seconds"""
  arrival_time: int
  """Arrival timestamp"""
  departure_time: int
  """Departure timestamp"""
  friendly_duration: str
  """Duration with units e.g. 37 mins"""
  friendly_arrival_time: str
  """Arrival time in the format HH:MM"""
  friendly_departure_time: str
  """Departure time in the format HH:MM"""

class BusInfo(Directions):
  bus_name: str
  bus_departure_time: int
  """Bus's departure timestamp from nearest stop"""

class Point(BaseModel):
  latitude: float
  longitude: float

  @staticmethod
  def from_string(point_str: str) -> 'Point':
    """ Expects a string in the format 'latitude,longitude' """
    try:
      lat_str, lon_str = point_str.split(',')
      return Point(latitude=float(lat_str), longitude=float(lon_str))
    except Exception as e:
      raise ValueError(f'Invalid point string: {point_str}. Expected format "latitude,longitude". Error: {str(e)}')

class TravelMode(StrEnum):
  BUS = 'bus'
