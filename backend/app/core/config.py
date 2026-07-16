import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:///./localhub.db")
    OPENAI_API_KEY: str = Field(default="")
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")
    # 길찾기(경로 안내) 기능용 카카오모빌리티 REST API 키
    KAKAO_REST_API_KEY: str = Field(default="")
    # 대중교통 길찾기(ODsay) API 키
    ODSAY_API_KEY: str = Field(default="")

    # 챗봇(CHT) 설정
    OPENAI_MODEL: str = Field(default="gpt-5-mini")
    OPENAI_TIMEOUT: float = Field(default=60.0)
    # i18n 번역용 모델 (장소 배치 번역 §C-1, UGC 온디맨드 번역 §C-2 공용)
    OPENAI_TRANSLATE_MODEL: str = Field(default="gpt-4o-mini")
    # 요청 시 함께 전송할 최근 대화 턴 수 상한 (명세 §7 비용 제약)
    CHAT_HISTORY_TURNS: int = Field(default=6)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
