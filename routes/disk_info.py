from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import shutil
from hurry.filesize import size

router = APIRouter(
  prefix='/disk',
  tags=['disk']
)

class Size(BaseModel):
  bytes: int
  human_readable: str

class DiskInfo(BaseModel):
  total: Size
  used: Size
  free: Size

@router.get('/', response_model=DiskInfo)
def get_disk_info() -> DiskInfo:

  total, used, free = shutil.disk_usage('/')

  def get_size_info(bytes: int) -> Size:
    return Size(
      bytes=bytes,
      human_readable=size(bytes)
    )

  return jsonable_encoder({
    "total": get_size_info(total),
    "used": get_size_info(used),
    "free": get_size_info(free)
  })
