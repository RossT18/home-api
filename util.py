from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel

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

  def get_iso(self):
    return f'{self.Y}-{self.m}-{self.d}'
  
  def get_datetime(self, tzinfo=ZoneInfo('Europe/London')):
    return datetime(int(self.Y), int(self.m), int(self.d), tzinfo=tzinfo)

  def __lt__(self, other: 'Date'):
    return self.get_datetime() < other.get_datetime()
  def __lt__(self, other: datetime):
    return self.get_datetime(other.tzinfo) < other
  
  def __gt__(self, other: 'Date'):
    return self.get_datetime() > other.get_datetime()
  def __gt__(self, other: datetime):
    return self.get_datetime(other.tzinfo) > other
  
  def __le__(self, other: 'Date'):
    return self.get_datetime() <= other.get_datetime()
  def __le__(self, other: datetime):
    return self.get_datetime(other.tzinfo) <= other
  
  def __ge__(self, other: 'Date'):
    return self.get_datetime() >= other.get_datetime()
  def __ge__(self, other: datetime):
    return self.get_datetime(other.tzinfo) >= other
  
  def __eq__(self, other: 'Date'):
    return self.get_datetime() == other.get_datetime()
  def __eq__(self, other: datetime):
    return self.get_datetime(other.tzinfo) == other
  
  def __ne__(self, other: 'Date'):
    return self.get_datetime() != other.get_datetime()
  def __ne__(self, other: datetime):
    return self.get_datetime(other.tzinfo) != other
  

def datetime_to_date(dt: datetime) -> Date:
  def get_suffix():
    day = int(dt.strftime('%d'))
    if 4 <= day <= 20 or 24 <= day <= 30:
      suffix = "th"
    else:
      suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix
  return Date(
    a=dt.strftime('%a'),
    A=dt.strftime('%A'),
    d=dt.strftime('%d'),
    b=dt.strftime('%b'),
    B=dt.strftime('%B'),
    m=dt.strftime('%m'),
    Y=dt.strftime('%Y'),
    s=get_suffix(),
  )

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

  return datetime_to_date(today)

def get_time() -> str:
  now = get_now()
  return now.strftime("%H:%M")

def is_in_past(date: str) -> bool:
  date_obj = datetime.strptime(date, "%Y-%m-%d").date()
  return date_obj < get_now().date()

def convert_ISO_to_dt(iso: str) -> Date:
  return datetime.strptime(iso, "%Y-%m-%d")
