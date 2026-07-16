from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    # i18n 배치 사전 번역 결과(translate_locations.py). 미번역 행은 NULL이며
    # 프론트가 locale에 따라 name/name_en, address/address_en 중 표시 필드를 선택한다.
    name_en = Column(String(255), nullable=True)
    address_en = Column(String(255), nullable=True)
