import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.comment import CommentOut

class PostBase(BaseModel):
    title: str
    content: str
    author: str

class PostCreate(PostBase):
    password: str  # 평문 비밀번호 (요구사항)
    image_url: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: str  # 본인확인용 평문 비밀번호

class PostOut(PostBase):
    id: int
    image_url: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True
