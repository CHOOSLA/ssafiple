import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class Translation(Base):
    """UGC 온디맨드 번역(POST /api/translate) 결과 캐시.

    같은 원문+대상언어 조합의 재번역(=OpenAI 재호출)을 막기 위한 캐시 테이블.
    source_hash = md5(text + target_lang) 이며 UNIQUE 제약으로 중복 저장을 차단한다.
    """
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    source_hash = Column(String(32), unique=True, nullable=False, index=True)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
