# LocalHub (서울)

서울 지역 관광지 정보 공유 및 인공지능 기반 여행 비서 서비스입니다.

---

## ⚠️ 프로젝트 중요 고지 사항 (명세 필수 기재)

### 1. 비밀번호 보관 및 검증 방식
* **비밀번호 평문 저장 및 비교**: 본 서비스는 회원가입 없이 게시글/댓글 작성 시 설정하는 비밀번호를 데이터베이스에 **평문(Plaintext)으로 저장**하고 비교합니다. 
* 실제 상용 서비스에서는 안전하지 않으나, 본 프로젝트의 제약 및 요구사항(단기 구현 목적)에 따라 이와 같이 구현되었습니다.

### 2. Kakao Maps JS SDK API Key 노출
* 프론트엔드 Vue.js 웹 애플리케이션의 특성상, 지도 렌더링에 사용되는 Kakao Maps API Key는 클라이언트 사이드 코드(브라우저)에 그대로 노출됩니다.
* 보안을 위해 카카오 개발자 콘솔에서 허용 도메인(예: `localhost`, `netlify.app`)을 엄격하게 제한해 두어야 합니다.

### 3. Render 무료 플랜의 휘발성 파일 시스템 주의
* 백엔드가 배포되는 Render의 Free Web Service 플랜은 영구 저장소를 지원하지 않습니다.
* 따라서 `backend/uploads/`에 업로드된 이미지 파일들은 **서비스가 재배포되거나 재시작될 때 모두 삭제(휘발)**됩니다. 실 서비스 운영 시에는 AWS S3 등 별도의 오브젝트 스토리지를 연동해야 합니다.

### 4. 공공누리 출처 표시 및 데이터 라이선스
* 본 서비스에 활용되는 서울시 관광지 정보 등의 데이터는 **공공데이터포털 및 서울열린데이터광장**을 출처로 합니다.
* 데이터 라이선스 및 구체적인 출처 목록은 [docs/SOURCE.md](file:///C:/SSAFY/00.StartCamp/team_project/docs/SOURCE.md)에서 확인하실 수 있습니다.

---

## 🔍 프로젝트 구조 및 검증 보고서

### 1. 과도한 구성 배제 (Over-Engineering 검증)
이틀이라는 촉박한 SSAFY 팀 프로젝트 납기 일정에 맞추어 **"고ROI(투자대비효과), 경량화"**를 목표로 설계를 검증했습니다.
* **경량 모노레포 지향**: `Nx`나 `Turborepo`, `pnpm workspace`와 같은 복잡한 오케스트레이션 도구는 FE/BE 언어 생태계가 다르고 패키지 공유 실익이 없어 도입하지 않았습니다. 대신 단일 Git Repository 내부에 `frontend/`와 `backend/` 디렉토리를 top-level로 분리해 관리의 단순성을 극대화했습니다.
* **SQLite 파일 DB 채택**: PostgreSQL이나 MySQL 같은 별도의 외부 데이터베이스 서버 인프라를 연동하는 것은 배포 및 로컬 세팅 환경을 복잡하게 하므로, SQLite 파일형 DB(`localhub.db`)를 채택하여 즉시 실행 가능하도록 구성했습니다.
* **단순화된 삭제 규칙**: SQLite FK Cascade 트리거 설정에 낭비되는 리소스를 아끼고 논리적 정합성을 유지하기 위해, 백엔드 애플리케이션 수준에서 **소프트 딜리트(Soft Delete) 연쇄 처리**를 구현하여 오버헤드를 줄였습니다.

### 2. 다인 개발 협업 준비도 (Multi-Developer Readiness 검증)
여러 명의 팀원이 코드를 클론 받아 동시에 개발하고 독립적으로 기능 개발을 수행할 수 있는 준비 태세를 검증했습니다.
* **완벽한 개발 환경 격리 (`.env.example` 제공)**: 
  개발환경에 따라 달라지는 API 주소나 카카오 지도 키, OpenAI API 키 등은 모두 `.env` 파일로 격리하여 소스코드 수정 없이 개발자별 로컬 환경 튜닝이 가능하게 하였습니다.
* **로컬 DB 즉시 복원 및 검증 장치 (`seed.py`)**:
  새로운 개발자가 프로젝트에 참여하더라도, `data/raw/` 폴더에 원본 JSON 데이터만 넣어준 뒤 `python backend/scripts/seed.py`를 실행하면 즉시 로컬 데이터베이스가 생성 및 초기화됩니다. 특히 위도/경도가 뒤바뀌는 에러를 사전에 막는 `assert` 장치도 탑재되어 있어 잘못된 데이터가 유입되지 않도록 안전장치를 마련했습니다.
* **협업을 위한 일관된 규칙 바인딩 ([AGENTS.md](file:///C:/SSAFY/00.StartCamp/team_project/AGENTS.md))**:
  AI 코딩 에이전트와 사람 개발자가 일관된 컨텍스트를 유지할 수 있도록, 지리적 좌표 범위, 소프트 딜리트 설계 제약, 그리고 **Git 커밋 스타일 규칙(콜론 앞뒤 공백 ` ) : ` 규격)**을 지침서로 공식 명문화하여 코드 및 커밋 꼬임 현상을 방지했습니다.

---

## 🛠️ 기술 스택 (Baseline)

* **Frontend**: Vue 3 (Vite, SPA), Pinia, Vue Router, Kakao Maps JS SDK
* **Backend**: FastAPI, SQLAlchemy, SQLite
* **AI Chatbot**: OpenAI API (GPT 모델 활용)
* **Deployment**: Netlify (Frontend), Render (Backend)

---

## 🚀 로컬 개발 퀵 스타트 가이드 (Quick Start)

### 1. Backend (FastAPI) 설정 및 실행
```bash
# 1. 백엔드 폴더 이동
cd backend

# 2. Python 가상환경 생성 및 활성화
python -m venv .venv
# Windows (Powershell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. 필수 패키지 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# 생성된 .env 파일 내에 실제 OPENAI_API_KEY 등을 기재합니다.

# 5. 로컬 데이터베이스 시딩 (JSON 8종 원본 파일을 data/raw/에 넣은 후 실행)
python scripts/seed.py

# 6. FastAPI 서버 실행
uvicorn app.main:app --reload
```
* 백엔드 API 서버는 기본적으로 `http://localhost:8000`에서 실행되며, 대화형 문서(Swagger)는 `http://localhost:8000/docs`에서 제공됩니다.

### 2. Frontend (Vue.js 3) 설정 및 실행
```bash
# 1. 프론트엔드 폴더 이동
cd frontend

# 2. 의존성 패키지 설치
npm install

# 3. 환경 변수 설정
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000
# VITE_KAKAO_MAP_KEY=카카오JS지도키기재

# 4. 로컬 개발 서버 구동
npm run dev
```
* 프론트엔드 앱은 기본적으로 `http://localhost:5173`에서 기동됩니다.
