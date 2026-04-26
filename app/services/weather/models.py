from pydantic import BaseModel


class Weather(BaseModel):
    sunrise: str
    sunset: str
    temperature: int
    weather: str
    icon: str


class WeatherType(BaseModel):
    name: str
    icon: str
