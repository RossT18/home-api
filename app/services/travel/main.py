from dotenv import load_dotenv
from app.services.travel.models import BusInfo
from fastapi import HTTPException
from typing import List, Dict
import requests
import urllib
import os
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

def get_directions_response(transit_mode):
  # TODO: Make origin/destination configurable
  secrets = {
    "gmaps_api_key": os.getenv('GOOGLE_MAPS_API_KEY'),
    "origin_lat": os.getenv('LAT'),
    "origin_lon": os.getenv('LON'),
    "destination_lat": os.getenv('CAMB_LAT'),
    "destination_lon": os.getenv('CAMB_LON')   
  }

  bad_secrets = list((name for name, value in secrets.items() if value is None))
  if len(bad_secrets) > 0:
    raise HTTPException(status_code=500, detail=f'Secret(s) {bad_secrets} could not be loaded')

  params_builder = {
    'key': secrets["gmaps_api_key"],
    'origin': f'{secrets["origin_lat"]},{secrets["origin_lon"]}',
    'destination': f'{secrets["destination_lat"]},{secrets["destination_lon"]}',
    'mode': 'transit',
    'transit_mode': transit_mode,
    'alternatives': 'true',
  }

  params_list = (f'{k}={urllib.parse.quote(v)}' for k, v in params_builder.items())
  params_string = '&'.join(params_list)

  url = f'https://maps.googleapis.com/maps/api/directions/json?{params_string}'
  r = requests.get(url)
  if r.status_code != 200:
    raise HTTPException(status_code=r.status_code, detail=f'Error retrieving travel information. Reason: {r.reason}')
  
  return r.json()

def get_friendly_time(timestamp, timezone) -> str:
  t = datetime.fromtimestamp(timestamp, ZoneInfo(timezone))
  return f'{str(t.hour).zfill(2)}:{str(t.minute).zfill(2)}'

def format_bus_directions_response(response) -> List[BusInfo]:
  # data['routes'] is an array of objects (these are route alternatives)
  # data['routes'][X]['legs'] is the only relevant information
  # ...['legs'] is an array which should contain one object (direct from origin to destination) referred to below as 'leg'
  # 'leg'['arrival_time']['value'] has timestamp
  # 'leg'['duration']['text'] is length of time (e.g. 37 mins) ['value'] contains seconds
  # 'leg'['steps'] is array of objects
  # 'step' should have an object with "travel_mode"=transit and a "transit_details" object. This contains the bus info
  # 'transit_details'['departure_time']['value'] UTC of time bus is due to be at the stop
  # 'transit_details'['line']['short_name'] is bus number
  # 'transit_details'['line']['color'] is bus colour (though it seems to be the same for bus n1 and n3 so maybe ignore this)


  """ Journey Info:
  { [bus_name: string]: {
          arrival_time: number
          duration: string    
          bus_departure_time: number
      }
  }
  """

  # TODO: Support all buses in response, or accept a list of preferred buses
  VALID_BUSES = ['8', 'A the busway']
  buses_info: Dict[str, BusInfo] = {}

  routes = response['routes']
  for route in routes:
    leg = route['legs'][0]
    arrival_time = int(leg['arrival_time']['value'])
    departure_time = int(leg['departure_time']['value'])
    duration = int(leg['duration']['value'])
    friendly_duration = leg['duration']['text']

    bus_departure_time = -1
    depart_time_zone = None
    bus_name = '0'

    for step in leg['steps']:
      if step['travel_mode'] != 'TRANSIT':
        continue
      transit_details = step['transit_details']
      bus_departure_time = int(transit_details['departure_time']['value'])
      depart_time_zone = transit_details['departure_time']['time_zone']
      bus_name = transit_details['line']['short_name']
      break

    invalid_bus = bus_departure_time <= 0 or bus_name not in VALID_BUSES
    earlier_bus_already_found = bus_name in buses_info and buses_info[bus_name].arrival_time < arrival_time

    if invalid_bus or earlier_bus_already_found:
      continue
    
    # Found a valid bus that is the earliest
    # Get the data and store it
    buses_info[bus_name] = BusInfo(
      bus_name=bus_name,
      bus_departure_time=bus_departure_time,
      duration=duration,
      arrival_time=arrival_time,
      departure_time=departure_time,
      friendly_duration=friendly_duration,
      friendly_arrival_time=get_friendly_time(arrival_time, depart_time_zone),
      friendly_departure_time=get_friendly_time(departure_time, depart_time_zone)
    )

  return list(buses_info.values())
