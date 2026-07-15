"""장소별 실시간 익명 채팅(FR-CHT §5.4) 서비스 계층.

AI 챗봇 서비스(app/services/chat.py)와는 무관한 별도 모듈로,
익명 닉네임 발급 및 채팅 메시지 영구 저장/조회만 담당합니다.
"""
import random
from typing import List

from sqlalchemy.orm import Session

from app.models import ChatMessage

ADJECTIVES = ["즐거운", "신비한", "용감한", "느긋한", "다정한", "엉뚱한", "씩씩한", "포근한"]
ANIMALS = ["여우", "너구리", "고양이", "펭귄", "다람쥐", "부엉이", "토끼", "수달"]


def generate_nickname() -> str:
    return f"익명 {random.choice(ADJECTIVES)}{random.choice(ANIMALS)}{random.randint(10, 99)}"


def save_message(db: Session, location_id: str, nickname: str, content: str) -> ChatMessage:
    message = ChatMessage(location_id=location_id, nickname=nickname, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_recent_messages(db: Session, location_id: str, limit: int = 50) -> List[ChatMessage]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.location_id == location_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(messages))
