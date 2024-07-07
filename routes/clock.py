from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import util as Util

router = APIRouter(
  prefix='/clock',
  tags=['clock']
)

@router.get('/', response_model=Util.DateTime)
def get_clock() -> Util.DateTime:
  return jsonable_encoder({
    "date": Util.get_date(),
    "time": Util.get_time()
  })

@router.get('/date', response_model=Util.Date)
def get_date() -> Util.Date:
  return Util.get_date()

@router.get('/time', response_model=str)
def get_time() -> str:
  return Util.get_time()
