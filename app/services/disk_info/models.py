from pydantic import BaseModel


class Size(BaseModel):
    bytes: int
    human_readable: str


class DiskSpace(BaseModel):
    total: Size
    used: Size
    free: Size
