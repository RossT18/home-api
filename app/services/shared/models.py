from pydantic import BaseModel


class Point(BaseModel):
    latitude: float
    longitude: float

    @staticmethod
    def from_string(point_str: str) -> "Point":
        """Expects a string in the format 'latitude,longitude'"""
        try:
            lat_str, lon_str = point_str.split(",")
            return Point(latitude=float(lat_str), longitude=float(lon_str))
        except Exception as e:
            raise ValueError(
                f'Invalid point string: {point_str}. Expected format "latitude,longitude". Error: {str(e)}'
            )
