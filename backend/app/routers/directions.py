from fastapi import APIRouter, HTTPException, Query

from app.schemas import CarDirectionsResponse, TransitDirectionsResponse
from app.services.directions import DirectionsError, get_car_directions, get_transit_directions

router = APIRouter(prefix="/directions", tags=["directions"])


@router.get("/car", response_model=CarDirectionsResponse)
def fetch_car_directions(
    origin_lat: float = Query(...),
    origin_lng: float = Query(...),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
):
    try:
        return get_car_directions(origin_lat, origin_lng, dest_lat, dest_lng)
    except DirectionsError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/transit", response_model=TransitDirectionsResponse)
def fetch_transit_directions(
    origin_lat: float = Query(...),
    origin_lng: float = Query(...),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
):
    try:
        return get_transit_directions(origin_lat, origin_lng, dest_lat, dest_lng)
    except DirectionsError as e:
        raise HTTPException(status_code=502, detail=str(e))
