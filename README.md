# SSAFIPLE (서울)
서울 지역 관광지 정보 공유 및 AI 여행 비서 서비스

---

## ⚠️ 프로젝트 중요 고지 사항
1. **비밀번호 평문 저장 및 비교**: 회원가입 없는 익명 게시판 구조로, 비밀번호는 암호화 없이 평문으로 DB에 저장·비교합니다.
2. **Kakao Maps Key 노출**: 클라이언트 브라우저 로드 특성상 키가 노출되므로, 카카오 콘솔에서 허용 도메인(`localhost`, 배포 도메인)을 필히 제한해야 합니다.
3. **Render 무료 플랜 휘발성**: Render의 파일시스템 제약으로 인해 `backend/uploads/` 내 업로드 파일은 재배포 시 삭제(휘발)됩니다.
4. **공공누리 제3유형**: 출처 표시 필수 및 내용 변경 금지 조건입니다. 서비스 푸터에 출처 표기 문안을 상시 노출해야 합니다.

---

## 📂 폴더 구조
```text
team_project/
├── docs/                      # 설계 문서 (SCHEMA.md, SOURCE.md)
├── data/raw/                  # 원본 공공데이터 JSON 파일 보관 (.gitkeep)
├── frontend/                  # Vue 3 프론트엔드
│   ├── src/
│   │   ├── router/            # Vue Router 설정 (페이지 라우팅)
│   │   ├── stores/            # Pinia 전역 스토어 (chat, modal, routeSelection)
│   │   └── pages/             # 화면 뷰 컴포넌트 5종
│   └── public/_redirects      # Netlify 새로고침 404 방지 라우팅 설정
└── backend/                   # FastAPI 백엔드
    ├── app/
    │   ├── core/config.py     # Pydantic Settings 기반 환경변수 로더
    │   ├── database.py        # SQLite 연결 & PRAGMA 설정
    │   ├── models/            # SQLAlchemy 모델 (is_deleted 소프트 딜리트 반영)
    │   ├── schemas/           # Pydantic DTO 검증 스키마
    │   └── routers/           # API 라우터 4종 (소프트 딜리트 CASCADE 연쇄 구현)
    └── scripts/seed.py        # 서울 범위 위경도 assert 검증 & DB 시딩 스크립트
```

---

## 🔍 프로젝트 검증 (경량화 및 협업 준비)
* **과도한 구성 배제**: Nx/Turborepo 등의 오케스트레이터를 걷어내고 폴더 구분만 둔 경량 단일 레포 구조입니다. 외부 DB가 필요 없는 파일 기반 SQLite를 사용합니다.
* **다인 협업 준비**: `.env.example`을 제공하여 로컬 설정을 격리하고, `seed.py` 실행만으로 로컬 DB 복원이 가능합니다. `AGENTS.md`를 통해 코딩 룰 및 깃 커밋 스타일(`Type(Scope) : 설명`)을 맞추어 협업 병목을 방지했습니다.

---

## 🚀 로컬 개발 퀵 스타트

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows 활성화 (macOS: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env         # 생성된 .env에 OpenAI API Key 등 기재
python scripts/seed.py       # 로컬 DB 생성 및 시딩
uvicorn app.main:app --reload
```
* **Swagger API Docs**: `http://localhost:8000/docs`

### 2. Frontend (Vue 3)
```bash
cd frontend
npm install
cp .env.example .env         # 생성된 .env에 Kakao Map Key 등 기재
npm run dev
```
* **로컬 웹 주소**: `http://localhost:5173`
