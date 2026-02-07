from app.util import get_date
from fastapi import HTTPException
from typing import List
import requests
import os
from dotenv import load_dotenv

from .models import BinSchedule, Collection

load_dotenv()

def get_bin_url_response():
  uprn = os.getenv('UPRN')
  if uprn is None:
    raise HTTPException(status_code=500, detail='Secret UPRN could not be loaded')
  url = f"https://servicelayer3c.azure-api.net/wastecalendar/collection/search/{uprn}/?authority=CCC/?numberOfCollections=12"
  r = requests.get(url)
  if r.status_code != 200:
    raise HTTPException(status_code=r.status_code, detail=f'Error retrieving bin schedule. Reason: {r.reason}') 
  return r.json()

def get_next_bin(collections: List[Collection]) -> Collection:
  today = get_date()
  today_iso = f'{today.Y}-{today.m}-{today.d}'
  for col in sorted(collections, key=lambda col: col.date):
    if col.date >= today_iso:
      return col
  raise HTTPException(status_code=404, detail='Next bin collection cannot be found')

def format_bin_schedule_response(data, length=5) -> BinSchedule:
  round_type_to_colour = {
    'DOMESTIC': 'black',
    'RECYCLE': 'blue',
    'ORGANIC': 'green',
    'FOOD': 'brown'
  }
  collections: List[Collection] = []
  for i in range(len(data['collections'])):
      if i >= length:
        break
      collection: Collection = data['collections'][i]

      collections.append(Collection(
        date=collection['date'][0:collection['date'].index('T')],
        bins=list(map(lambda rt: round_type_to_colour[rt], collection['roundTypes']))
      ))


  return BinSchedule(
    collections=collections,
    next=get_next_bin(collections)
  )
