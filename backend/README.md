# SSAFIPLE Backend

이 디렉토리는 SSAFIPLE (서울 권역 지역 정보 공유 커뮤니티)의 **FastAPI 백엔드 서버** 소스코드를 포함하고 있습니다.

## 🛠️ 기술 스택
* **Framework**: FastAPI (Python 3)
* **ORM / Database**: SQLAlchemy / SQLite (무설치 로컬 DB)
* **Dependencies**: Uvicorn, Pydantic, Python-dotenv 등 (상세 버전은 `requirements.txt` 참조)

## 📂 디렉토리 구조
* `app/core/`: Pydantic 기반 설정(`config.py`) 및 보안 로직
* `app/models/`: SQLAlchemy 데이터베이스 모델 스키마 (장소, 게시판, 댓글 등)
* `app/schemas/`: API 요청/응답 검증을 위한 Pydantic DTO 스키마
* `app/routers/`: 기능 도메인별 분리된 API 엔드포인트 (`locations.py`, `posts.py`, `chat.py` 등)
* `app/services/`: 비즈니스 로직 및 AI(OpenAI) 처리 계층
* `app/database.py`: SQLite 연동 및 DB 세션 생성기
* `scripts/`: 데이터 초기화 및 검증용 유틸리티 (`seed.py`)

## ⚙️ 환경 변수 (.env)
루트 디렉토리의 `.env.example` 파일을 복사하여 `.env` 파일을 생성하고 다음 변수들을 채워야 합니다.
```env
# 기본 설정
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# AI 챗봇 기능을 위한 OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 실행 방법

### 1. 가상환경 및 의존성 설치
```bash
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 데이터베이스 초기화 (Seeding)
공공데이터 JSON 파일을 바탕으로 SQLite DB(`localhub.db`)를 생성하고 기초 장소 데이터를 주입합니다.
```bash
python scripts/seed.py
```

### 3. 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```
서버 실행 후, `http://localhost:8000/docs` 로 접속하면 자동으로 생성된 **Swagger API 명세서**를 통해 모든 API를 테스트할 수 있습니다.
