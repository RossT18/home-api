from app.services.disk_info.main import get_disk_space
from app.services.disk_info.models import DiskSpace
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder


router = APIRouter(
  prefix='/disk',
  tags=['disk']
)


@router.get('/', response_model=DiskSpace)
def get_disk_info() -> DiskSpace:
  return jsonable_encoder(get_disk_space())
