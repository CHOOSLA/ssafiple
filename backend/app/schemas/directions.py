from typing import List, Literal, Optional
from pydantic import BaseModel


class RoutePoint(BaseModel):
    lat: float
    lng: float


class CarRouteCandidate(BaseModel):
    label: str
    path: List[RoutePoint]
    duration: int  # 예상 소요 시간 (초)
    distance: int  # 이동 거리 (미터)


class CarDirectionsResponse(BaseModel):
    candidates: List[CarRouteCandidate]


class TransitSegment(BaseModel):
    mode: Literal["walk", "bus", "subway"]
    label: Optional[str] = None
    start_name: str
    end_name: str
    duration: int  # 구간 소요 시간 (초)
    distance: int  # 구간 거리 (미터)
    path: List[RoutePoint]


class TransitRouteCandidate(BaseModel):
    duration: int  # 총 소요 시간 (초)
    distance: int  # 총 이동 거리 (미터)
    transfer_count: int
    walk_distance: int
    segments: List[TransitSegment]


class TransitDirectionsResponse(BaseModel):
    candidates: List[TransitRouteCandidate]
