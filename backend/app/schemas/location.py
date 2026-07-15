from pydantic import BaseModel
from typing import Optional

class LocationBase(BaseModel):
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationOut(LocationBase):
    id: int
    post_count: Optional[int] = 0
    latest_post_title: Optional[str] = None

    class Config:
        from_attributes = True
