import datetime
from pydantic import BaseModel

class CommentBase(BaseModel):
    content: str
    author: str

class CommentCreate(CommentBase):
    password: str  # 평문 비밀번호 (요구사항)

class CommentOut(CommentBase):
    id: int
    post_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
