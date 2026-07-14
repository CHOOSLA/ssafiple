# SSAFIPLE 팀 협업 및 브랜치 전략 (COOPERATION.md)

본 문서는 3인의 개발자가 프로젝트 명칭 **SSAFIPLE** 및 전달받은 디자인 초안을 바탕으로, 충돌(Conflict) 없이 신속하게 병합(Merge)할 수 있도록 설계한 기능 분배 및 브랜치 가이드라인입니다.

---

## 🎨 디자인 초안 스타일 분석 요약
* **메인 컬러 테마**:
  * 배경색: `#eef0ea` (안정적인 올리브 라이트 그레이)
  * 포인트(Accent) 컬러: `#f15b4c` (활기찬 피치 오렌지)
  * 카테고리별 마커 컬러: 관광지 `#f15b4c`, 음식점 `#ef8a3c`, 문화시설 `#3f8fd0`, 쇼핑 `#8a6fd6`, 숙박 `#5aa06a`
* **UI/UX 구조**:
  * **좌측 60% 영역**: 스플릿 패널 (장소 목록 카드, 장소 상세 탭(글/채팅 분리), 글쓰기 폼, 게시글 상세)
  * **우측 40% 영역**: 지도 뷰포트 (드래그, 줌, 장소 핀 마커 및 커스텀 오버레이 말풍선)
  * **글로벌 플로팅 위젯**: 우측 하단 AI 여행 도우미 챗봇 팝업 창

---

## 👥 3인 기능 분배 및 브랜치 전략
Git Merge 시 코드 충돌을 예방하기 위해 **파일 및 컴포넌트 단위를 엄격히 분리**하여 개발을 진행합니다.

### 👨‍💻 개발자 A (프론트엔드 - 지도 및 지리 정보)
* **주요 역할**: 
  * Kakao Maps JS SDK 연동 및 지도 화면 구현 (`/map`)
  * 지도 상의 카테고리별 핀 마커 렌더링, 오버레이 말풍선 매핑
  * 좌측 패널의 장소 목록 카드 렌더링 및 카테고리 필터링
  * **[Phase 2] 경로 안내 모드 (마커 다중 선택, Polyline 연결 및 거리 합계 시각화)**
* **작업 브랜치**: `feat/fe-map`
* **독점 작업 파일**:
  * `frontend/src/pages/MapView.vue`
  * `frontend/src/stores/routeSelection.js`
* **충돌 방지 약속**: 게시판 뷰포트 및 챗봇 위젯 코드는 손대지 않고, 지도 연동에만 집중합니다.

---

### 👩‍💻 개발자 B (프론트엔드/백엔드 - 게시판 CRUD)
* **주요 역할**:
  * 자유게시판의 게시글 및 댓글 CRUD API 보완
  * 익명 작성 시 수정용 평문 비밀번호 검증 로직 매핑
  * 게시글 목록(검색 및 페이지네이션 포함), 상세조회(댓글 목록 포함), 작성/수정 폼 화면 개발
  * **[Phase 2] 게시글 이미지 첨부 (Multipart/form-data 업로드 및 정적 파일 서빙)**
* **작업 브랜치**: `feat/board-crud`
* **독점 작업 파일**:
  * `frontend/src/pages/PostListView.vue`, `PostDetailView.vue`, `PostEditView.vue`
  * `frontend/src/stores/modal.js`
  * `backend/app/routers/posts.py`, `comments.py`
  * `backend/app/models/post.py`, `comment.py`
* **충돌 방지 약속**: 백엔드 라우터에서 게시판 API에만 기여하고, 챗봇 및 세부 시딩 스크립트는 터치하지 않습니다.

---

### 👨‍💻 개발자 C (백엔드/프론트엔드 - 데이터 시딩 & AI 챗봇)
* **주요 역할**:
  * `data/raw/` 원본 JSON 8종 파싱 및 `seed.py` 적재 스크립트 구체화
  * OpenAI API 연동 및 `/api/chat` 엔드포인트 구현 (추후 CHT-01 컨텍스트 필터 적용 예정)
  * 프론트엔드 공통 플로팅 AI 챗봇 위젯 컴포넌트 구현 및 스크립트 연결
* **작업 브랜치**: `feat/be-chatbot-seed`
* **독점 작업 파일**:
  * `backend/scripts/seed.py`
  * `backend/app/routers/chat.py`
  * `backend/app/models/location.py`
  * `frontend/src/stores/chat.js`
  * `frontend/src/App.vue` (챗봇 전역 플로팅 연동부만 수정)
* **충돌 방지 약속**: 프론트엔드 `App.vue`에서 챗봇 관련 마크업/이벤트 영역만 안전하게 수정하고, 지도 및 게시판의 개별 화면은 건드리지 않습니다.

---

## 🏗️ 브랜치 분기 시점 및 초기 공통 구성 (Base Setup)
본격적인 3인 병렬 개발(`feat/...` 브랜치 분할)을 시작하기 전, `master` 브랜치에 다음의 **공통 뼈대(Scaffolding)**가 모두 구성되어 있어야 합니다. 이 작업이 선행된 이후에 각자의 브랜치로 나뉘어야 충돌을 최소화할 수 있습니다.

* **[백엔드] 공통 뼈대 구성**:
  * FastAPI 앱 팩토리 및 라우터 기본 구조 (`main.py`, `routers/`)
  * SQLite 연동을 위한 SQLAlchemy 기본 설정 (`database.py`)
  * `posts`, `comments`, `locations` 테이블 생성을 위한 기본 모델 구조 (`models/`)
  * 공통 환경변수 템플릿 (`.env.example`) 공유
* **[프론트엔드] 공통 뼈대 구성**:
  * Vue Router 초기화 및 주요 뷰 빈 컴포넌트 뼈대 생성 (`MapView.vue`, `PostListView.vue`, `PostDetailView.vue` 등)
  * 디자인 시스템 연동: 글로벌 CSS 변수(`--accent: #f15b4c`, 배경색 등) 및 Pretendard 폰트가 적용된 `style.css` 
  * Pinia Store 및 전역 Axios 인스턴스 초기화

> **✨ 브랜치 분기 시점 (When to Branch)**:
> 위의 기초 뼈대 코드가 `master` 브랜치에 모두 병합된 직후, 각 개발자는 `git checkout -b feat/...`를 실행하여 자신의 기능 개발을 시작합니다.

---

## 🔀 Git Workflow & Merge 규칙
1. **브랜치 생성**: 반드시 `master` 브랜치로부터 각자의 피처 브랜치(`feat/...`)를 생성합니다.
2. **독립 개발**: 위의 독점 작업 파일 가이드를 준수하며 서로의 작업 영역을 침범하지 않도록 코딩합니다.
3. **로컬 교차 검증**:
   * 로컬에 `localhub.db` 파일이 생성되므로, DB 스키마 수정(개발자 B)이 있을 경우 시드 스크립트(개발자 C)도 즉시 업데이트하여 싱크를 맞춥니다.
4. **Merge 전 Pull**:
   * `master` 브랜치에 코드가 합쳐지면, 자신의 브랜치에서 `git pull origin master`를 실행해 최신 로컬 상태를 동기화하고 충돌 여부를 자가 진단한 후 PR(Pull Request)을 날려 병합합니다.
