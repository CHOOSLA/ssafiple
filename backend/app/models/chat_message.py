import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String(50), index=True, nullable=False)  # 장소별 실시간 채팅방 구분용
    nickname = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
