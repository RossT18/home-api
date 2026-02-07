from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from app.util import Date, DateTime, get_date, get_time


router = APIRouter(
  prefix='/clock',
  tags=['clock']
)

@router.get('/', response_model=DateTime)
def get_current_datetime() -> DateTime:
  return jsonable_encoder({
    "date": get_date(),
    "time": get_time()
  })

@router.get('/date', response_model=Date)
def get_current_date() -> Date:
  return get_date()

@router.get('/time', response_model=str)
def get_current_time() -> str:
  return get_time()
