from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel

router = APIRouter(
  prefix='/clock',
  tags=['clock']
)

class Date(BaseModel):
  a: str
  """Short day name""" 
  A: str
  """Long day name"""
  d: str
  """Date"""
  b: str
  """Short month name"""
  B: str
  """Long month name"""
  m: str
  """Month"""
  Y: str
  """Year"""
  s: str
  """Date suffix"""

class DateTime(BaseModel):
  date: Date
  time: str

def get_now() -> datetime:
  return datetime.now(ZoneInfo('Europe/London'))

def get_date() -> Date:
  today = get_now()
  # 'a': 'Wed',
  # 'A': 'Wednesday',
  # 'd': '22',
  # 'b': 'Sep',
  # 'B': 'September',
  # 'm': '09',
  # 'Y': '2024',
  # 's': 'nd'

  def get_suffix():
    day = int(today.strftime('%d'))
    if 4 <= day <= 20 or 24 <= day <= 30:
      suffix = "th"
    else:
      suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix
  
  return Date(
    a=today.strftime('%a'),
    A=today.strftime('%A'),
    d=today.strftime('%d'),
    b=today.strftime('%b'),
    B=today.strftime('%B'),
    m=today.strftime('%m'),
    Y=today.strftime('%Y'),
    s=get_suffix(),
  )

def get_time() -> str:
  now = get_now()
  return now.strftime("%H:%M")

@router.get('/', response_model=DateTime)
def get_clock() -> DateTime:
  return jsonable_encoder({
    "date": get_date(),
    "time": get_time()
  })

@router.get('/date', response_model=Date)
def api_get_date() -> Date:
  return get_date()

@router.get('/time', response_model=str)
def api_get_time() -> str:
  return get_time()