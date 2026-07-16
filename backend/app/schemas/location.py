from pydantic import BaseModel
from typing import Optional, List

class PostPreview(BaseModel):
    id: int
    title: str
    snippet: str
    comment_count: int

class LocationBase(BaseModel):
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    # 배치 사전 번역된 영문 명칭/주소(미번역 시 null) — 프론트가 locale에 맞춰 선택
    name_en: Optional[str] = None
    address_en: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationOut(LocationBase):
    id: int
    post_count: Optional[int] = 0
    latest_posts: List[PostPreview] = []

    class Config:
        from_attributes = True
