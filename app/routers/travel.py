from app.services.shared.models import Point
from app.services.travel.main import (
    get_directions_response,
    format_bus_directions_response,
)
from app.services.travel.models import BusInfo, TravelMode
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from typing import List


router = APIRouter(prefix="/travel", tags=["travel"])


@router.get("/bus/{origin}/{destination}", response_model=List[BusInfo])
def get_bus_journey_info(
    origin: str, destination: str, accepted_buses: str | None = None
) -> List[BusInfo]:
    origin_point = Point.from_string(origin)
    destination_point = Point.from_string(destination)
    formatted_accepted_buses = accepted_buses.split(",") if accepted_buses else []

    bus_directions_response = get_directions_response(
        TravelMode.BUS, origin_point, destination_point
    )
    formatted = format_bus_directions_response(
        bus_directions_response, formatted_accepted_buses
    )
    return jsonable_encoder(formatted)
