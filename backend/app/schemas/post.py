import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.comment import CommentOut

class PostImageOut(BaseModel):
    id: int
    image_url: str
    display_order: int

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    author: str
    location_id: Optional[str] = None

class PostCreate(PostBase):
    password: str  # 평문 비밀번호 (요구사항)
    image_url: Optional[str] = None
    # 여러 장 등록 시 사용. 값이 있으면 image_url(대표 이미지)은 첫 번째 항목으로 자동 지정됨
    image_urls: Optional[List[str]] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: str  # 본인확인용 평문 비밀번호

class PostOut(PostBase):
    id: int
    image_url: Optional[str] = None
    images: List[PostImageOut] = []
    created_at: datetime.datetime
    updated_at: datetime.datetime
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True
