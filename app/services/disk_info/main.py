import shutil
from .models import DiskSpace, Size
from hurry.filesize import size
  

def get_size_info(bytes: int) -> Size:
  return Size(
    bytes=bytes,
    human_readable=size(bytes)
  )

def get_disk_space() -> DiskSpace:
  total, used, free = shutil.disk_usage('/')

  return DiskSpace(
    total=get_size_info(total),
    used=get_size_info(used),
    free=get_size_info(free)
  )
