from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database import engine, Base, ensure_runtime_columns
from app.models import Location, Post, Comment, ChatMessage, Translation
from app.routers import posts, comments, locations, chat, directions, translate
import sys, os

# backend/ 경로를 sys.path에 추가하여 scripts 패키지를 가져올 수 있도록 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.seed import seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 DB 테이블 생성 (SQLite를 사용하므로 간편하게 자동 생성 처리)
    Base.metadata.create_all(bind=engine)
    # 기존 DB 파일에 나중에 추가된 컬럼(locations.name_en/address_en) 보강
    ensure_runtime_columns()
    # Render 휘발성 DB 대비 Auto-seeding
    try:
        seed_data()
    except Exception as e:
        print(f"Error during auto-seeding: {e}")
    yield

app = FastAPI(
    title="SSAFIPLE API",
    description="서울 지역 관광지 정보 공유 및 AI 여행 비서 서비스 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (프론트엔드 Vue 앱 도메인 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록 (기능명세서 §4.1 규격에 맞춰 모든 엔드포인트를 /api 하위로 통일)
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(directions.router, prefix="/api")
app.include_router(translate.router, prefix="/api")

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SSAFIPLE API",
        "version": "1.0.0"
    }
