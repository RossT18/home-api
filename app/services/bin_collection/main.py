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

def format_bin_schedule_response(data, length=5) -> BinSchedule:
  sorted_collections = sorted(data['collections'], key=lambda col: col['date'])
  
  today = get_date()
  today_iso = f'{today.Y}-{today.m}-{today.d}'
  # Filter out past collections, keeping only those that are today or in the future
  filtered_collections = list(filter(lambda col: col['date'] >= today_iso, sorted_collections))[:length]

  collections: List[Collection] = list(map(lambda raw: Collection(
    date=raw['date'][0:raw['date'].index('T')], # Extract the date part of the ISO string
    bins=raw['roundTypes']
  ), filtered_collections))

  if len(collections) == 0:
    raise HTTPException(status_code=404, detail='No upcoming bin collections found')

  return BinSchedule(collections=collections, next=collections[0])
