import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String(50), index=True, nullable=True) # 장소별 게시판 분류용
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)  # 평문 비밀번호 (요구사항)
    image_url = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # soft delete 로직 처리를 위해 cascade orphan 삭제 규칙 제외 및 active 댓글만 가져오도록 primaryjoin 적용
    comments = relationship(
        "Comment",
        primaryjoin="and_(Post.id==Comment.post_id, Comment.is_deleted==False)",
        back_populates="post"
    )
 