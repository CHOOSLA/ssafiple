# SSAFIPLE (서울)
서울 지역 관광지 정보 공유 및 AI 여행 비서 서비스

* **핵심 기능**: 카카오 지도 장소 탐색, 익명 게시판 CRUD, AI 챗봇 비서, **장소별 실시간 익명 채팅(WebSocket)**

---

## ⚠️ 프로젝트 중요 고지 사항
1. **비밀번호 평문 저장 및 비교**: 회원가입 없는 익명 게시판 구조로, 비밀번호는 암호화 없이 평문으로 DB에 저장·비교합니다.
2. **Kakao Maps Key 노출**: 클라이언트 브라우저 로드 특성상 키가 노출되므로, 카카오 콘솔에서 허용 도메인(`localhost`, 배포 도메인)을 필히 제한해야 합니다.
3. **Render 무료 플랜 휘발성**: Render의 파일시스템 제약으로 인해 `backend/uploads/` 내 업로드 파일은 재배포 시 삭제(휘발)됩니다.
4. **공공누리 제3유형**: 출처 표시 필수 및 내용 변경 금지 조건입니다. 서비스 푸터에 출처 표기 문안을 상시 노출해야 합니다.

---

## 📂 폴더 구조 (도메인별 풀스택 적용)
```text
team_project/
├── docs/                      # 설계 문서 (SCHEMA, SOURCE, 기능명세서 등)
├── data/raw/                  # 원본 공공데이터 JSON 파일
├── frontend/                  # Vue 3 프론트엔드
│   ├── src/
│   │   ├── components/        # 도메인별 분리된 UI 컴포넌트 (map, board, chat, common)
│   │   ├── pages/             # 화면 뷰 컴포넌트
│   │   ├── router/            # Vue Router 설정
│   │   ├── stores/            # Pinia 전역 스토어 (mapStore, boardStore, chatStore)
│   │   └── utils/             # 프론트엔드 공통 유틸 (api.js 등)
│   └── public/_redirects      # Netlify 새로고침 404 방지
└── backend/                   # FastAPI 백엔드
    ├── app/
    │   ├── core/config.py     # 환경변수 로더
    │   ├── database.py        # SQLite 연결 
    │   ├── models/            # SQLAlchemy DB 모델
    │   ├── schemas/           # Pydantic DTO (데이터 검증)
    │   ├── routers/           # FastAPI 도메인별 API 라우터
    │   ├── services/          # 비즈니스 로직 (chat_service, seed_service 등)
    │   └── utils/             # 백엔드 공통 유틸 (websocket_manager 등)
    └── scripts/seed.py        # DB 시딩 스크립트
```

---

## 🔍 프로젝트 검증 (경량화 및 협업 준비)
* **과도한 구성 배제**: Nx/Turborepo 등의 오케스트레이터를 걷어내고 폴더 구분만 둔 경량 단일 레포 구조입니다. 외부 DB가 필요 없는 파일 기반 SQLite를 사용합니다.
* **🤖 AI 주도 기능별 풀스택 개발 (Vertical Slicing)**: AI 에이전트(혹은 AI+사람 페어)가 개발을 주도하는 환경에 맞춰, 프론트/백엔드 레이어 분할이 아닌 **"도메인 기능별 풀스택 분할"**을 채택했습니다. 
  * `지도 도메인`, `게시판 도메인`, `챗봇/채팅 도메인` 3가지 브랜치로 분리하여 각 도메인의 FE 뷰포트부터 BE 라우터, DB 모델까지 완벽히 독립적으로 개발하여 맥락(Context)을 유지하고 병합 충돌을 원천 차단합니다.
* **다인 협업 준비**: `.env.example`을 제공하여 로컬 설정을 격리하고, `seed.py` 실행만으로 로컬 DB 복원이 가능합니다. `AGENTS.md`를 통해 코딩 룰 및 깃 커밋 스타일(`Type(Scope) : 설명`)을 맞추어 협업 병목을 방지했습니다.

---

## 🚀 프로덕션 배포 및 CI/CD (GitHub 미러링)
* **프론트엔드 (Netlify)**: `netlify.toml` 및 SPA 리다이렉트(`public/_redirects`) 설정 완료.
* **백엔드 (Render)**: FastAPI Uvicorn 배포를 위한 `render.yaml` 설정 완료.
* **GitLab CI 자동화**: `.gitlab-ci.yml`을 통해 내부 GitLab에서 GitHub 원격 저장소로 **자동 동기화(Mirroring)**를 수행합니다. 
  * 설정 방법: GitLab 설정 -> CI/CD -> Variables에 `GITHUB_USERNAME`, `GITHUB_PAT`, `GITHUB_REPO_NAME`을 등록하면 푸시 때마다 GitHub로 자동 배달됩니다.

---

## 💻 로컬 개발 퀵 스타트

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
* **Swagger API 명세서**: `http://localhost:8000/docs` (API 설계 및 테스트 지원)

### 2. Frontend (Vue 3)
```bash
cd frontend
npm install
cp .env.example .env         # 생성된 .env에 Kakao Map Key 등 기재
npm run dev
```
* **로컬 프론트 웹**: `http://localhost:5173`
* **🎨 프론트엔드 디자인 시스템 및 공통 컴포넌트 예제**: `http://localhost:5173/example`
