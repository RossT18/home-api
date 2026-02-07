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