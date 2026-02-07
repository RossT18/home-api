from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from app.services.bin_collection import BinSchedule, get_bin_url_response, format_bin_schedule_response


router = APIRouter(
  prefix='/bins',
  tags=['bins']
)

@router.get('/', response_model=BinSchedule)
def get_bin_schedule() -> BinSchedule:
  bin_schedule_response = get_bin_url_response()
  formatted = format_bin_schedule_response(bin_schedule_response, 5)
  return jsonable_encoder(formatted)
