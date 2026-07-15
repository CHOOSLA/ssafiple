# SSAFIPLE 테스트 명세서 (단위/통합)

기준 커밋: `0e26a9d` (2026-07-15). 백엔드 FastAPI + SQLite, 프론트 Vue 3 SPA. 모든 API는 `/api` prefix 하위에 등록됨 (`backend/app/main.py`).

## 0. 테스트 환경

| 항목 | 값 |
|---|---|
| 백엔드 실행 | `cd backend && python -m uvicorn app.main:app --reload` (http://localhost:8000) |
| 프론트 실행 | `cd frontend && npm run dev` (http://localhost:5173) |
| 단위/통합 테스트 실행 | `cd backend && python -m unittest discover -s tests -v` (`pytest` 미설치, 표준 `unittest` 사용) |
| DB | `backend/localhub.db` (SQLite 파일, 앱 시작 시 `Base.metadata.create_all` + `seed_data()` auto-seed) |
| 인증 | 없음 (전 구간 익명) |
| 게시판 비밀번호 | 의도적으로 평문 저장/비교 (교육 목적 명세, 취약점 아님) |

기존 테스트 자산: `backend/tests/test_post_image_upload.py` 1건만 존재. 아래 명세는 이를 확장하는 기준.

---

## 1. 단위 테스트 (Unit Test)

FastAPI `TestClient` + SQLite 파일 DB를 그대로 쓰는 구조라, "순수 단위 테스트"보다는 **라우터 함수 단위의 격리된 케이스**로 정의합니다. DB 부수효과가 걱정되면 각 테스트 앞뒤로 생성한 리소스를 정리(delete)하거나, `DATABASE_URL`을 `sqlite:///./test.db`로 오버라이드해서 별도 파일을 쓰는 걸 권장합니다.

### 1.1 Board 도메인 — `backend/app/routers/posts.py`, `comments.py`

| ID | 대상 함수 | 케이스 | 입력 | 기대 결과 |
|---|---|---|---|---|
| UT-POST-01 | `create_post` | 정상 생성 | title/content/author/password 모두 채움 | 201, `is_deleted=False`, `id` 발급 |
| UT-POST-02 | `create_post` | `location_id` 없이 생성 | location_id 생략 | 201, `location_id=null` (전역 취급) |
| UT-POST-03 | `list_posts` | `location_id` 필터 | 서로 다른 location_id 2건 생성 후 하나만 조회 | 필터링된 1건만 반환 |
| UT-POST-04 | `list_posts` | soft-delete된 글 제외 | 삭제 처리 후 목록 조회 | 목록에 미노출 |
| UT-POST-05 | `get_post` | 존재하지 않는 id | `GET /api/posts/999999` | 404 |
| UT-POST-06 | `update_post` | 비밀번호 불일치 | 틀린 password로 PUT | 403 |
| UT-POST-07 | `update_post` | 정상 수정 | 올바른 password, title만 변경 | 200, title만 반영 |
| UT-POST-08 | `delete_post` | 비밀번호 불일치 | 틀린 `password_in` | 403, `is_deleted` 그대로 False |
| UT-POST-09 | `delete_post` | 정상 삭제 + **CASCADE** | 댓글 2개 달린 글 삭제 | 204, 해당 글의 댓글도 모두 `is_deleted=True` |
| UT-POST-10 | `verify_post_password` | 정상/오류 각각 | 맞는/틀린 password | 200 vs 403 |
| UT-POST-11 | `upload_image` | 허용 확장자 | `.png` 업로드 | 200, `image_url`이 `/uploads/`로 시작 |
| UT-POST-12 | `upload_image` | 비허용 확장자 | `.exe` 업로드 | 400 |
| UT-POST-13 | `upload_image` | 파일명 없음 | `filename=""` | 400 |
| UT-COMMENT-01 | `create_comment` | 존재하지 않는 post_id | 삭제되었거나 없는 post_id | 404 |
| UT-COMMENT-02 | `create_comment` | 정상 생성 | 유효 post_id + 필드 | 201 |
| UT-COMMENT-03 | `delete_comment` | 비밀번호 불일치 | 틀린 password_in | 403 |
| UT-COMMENT-04 | `delete_comment` | 정상 삭제 | 올바른 password_in | 204, `is_deleted=True` (물리삭제 아님) |
| UT-COMMENT-05 | 목록 필터링 | 삭제된 댓글 미노출 | `GET /api/posts/{id}` 응답의 `comments` 배열 확인 | soft-delete된 댓글 제외됨 (Post 모델 `primaryjoin` 검증) |

### 1.2 Map 도메인 — `backend/app/routers/locations.py`

| ID | 케이스 | 입력 | 기대 결과 |
|---|---|---|---|
| UT-LOC-01 | `category` 필터 | `?category=관광지` | 해당 카테고리만 반환 |
| UT-LOC-02 | `q` 검색 | `?q=경복궁` | name/address `LIKE` 매칭 |
| UT-LOC-03 | Bounding box 필터 | `sw_lat/sw_lng/ne_lat/ne_lng` 지정 | 범위 내 좌표만 반환 |
| UT-LOC-04 | `limit` 상한 동작 | `?limit=10` | 정확히 ≤10건 |
| UT-LOC-05 | 전체 응답 금지 확인 | limit 미지정 | 기본값(50)으로 제한되는지 확인 (feature.md §5.3 "일괄 응답 금지") |
| UT-LOC-06 | 단건 조회 실패 | 존재하지 않는 id | 404 "관광지 정보를 찾을 수 없습니다." |
| UT-LOC-07 | seed 데이터 좌표 검증 | `backend/scripts/seed.py` | 서울 경계 assert (`126.75≤lng≤127.20`, `37.40≤lat≤37.72`) 위반 시 적재 실패하는지 |

### 1.3 Chat 도메인 — `backend/app/routers/chat.py`, `services/chat.py`

| ID | 케이스 | 입력 | 기대 결과 |
|---|---|---|---|
| UT-CHAT-01 | 빈 메시지 거절 | `message=""` | 422 (Pydantic `min_length=1`) |
| UT-CHAT-02 | 500자 초과 거절 | `message`가 501자 | 422 (`max_length=500`) |
| UT-CHAT-03 | 정상 응답 | 유효 message, 빈 history | 200, `reply` 문자열 반환 (OpenAI 키 필요 — mock 권장) |
| UT-CHAT-04 | OpenAI 예외 처리 | OpenAI API 장애/키 오류 mock | 502, "AI 응답 생성에 실패했습니다..." |
| UT-CHAT-05 | 히스토리 턴 제한 | history 10턴 이상 전송 | `CHAT_HISTORY_TURNS=6` 만큼만 컨텍스트에 포함되는지 (`services/chat.py` 내부 로직 검증) |
| UT-CHAT-06 | ⚠️ WebSocket 실시간 채팅 | — | **미구현** (`backend/app/utils/websocket_manager.py` 빈 파일, 라우터 미등록). 테스트 작성 보류, feature.md §5.4 추후 구현 대상 |

### 1.4 공통/모델 레벨

| ID | 케이스 | 기대 결과 |
|---|---|---|
| UT-MODEL-01 | `Post.comments` relationship | `primaryjoin`에 `Comment.is_deleted==False` 조건 포함 → 삭제된 댓글이 relationship 결과에서 제외되는지 |
| UT-MODEL-02 | `Comment.post_id` FK `ondelete="CASCADE"` | SQLAlchemy 레벨 설정 확인 (실제 DB는 소프트 딜리트라 이 CASCADE는 SQLite에서 미발동 — 서비스 로직의 수동 cascade와 혼동 주의) |
| UT-DB-01 | 로컬 DB 스키마 ↔ 모델 정합성 | `sqlite3 localhub.db ".schema posts"` 결과가 `models/post.py` 컬럼과 일치하는지 (과거 `location_id` 컬럼 누락으로 500 발생한 전례 있음 — 회귀 방지용) |

---

## 2. 통합 테스트 (Integration / E2E API Test)

`TestClient(app)`로 실제 앱 인스턴스를 띄워 여러 엔드포인트를 연쇄 호출하는 시나리오. 모든 경로는 `/api` prefix 포함.

### IT-01. 게시글 전체 생명주기 (CRUD + Cascade)
1. `POST /api/posts/` → 201, id 획득
2. `GET /api/posts/{id}` → 200, 방금 만든 내용과 일치
3. `POST /api/comments/?post_id={id}` (2건) → 각각 201
4. `GET /api/posts/{id}` → `comments` 배열에 2건 포함
5. `PUT /api/posts/{id}` (틀린 비번) → 403
6. `PUT /api/posts/{id}` (맞는 비번, title 변경) → 200
7. `DELETE /api/posts/{id}` (틀린 비번) → 403
8. `DELETE /api/posts/{id}` (맞는 비번) → 204
9. `GET /api/posts/{id}` → 404
10. `GET /api/posts/` 목록에 없는지 확인
11. **DB 직접 조회**: 댓글 2건의 `is_deleted`가 모두 `True`인지 (물리 삭제 아님을 증명)

### IT-02. 이미지 첨부 게시글 플로우
1. `POST /api/posts/upload-image` (정상 이미지) → 200, `image_url` 획득
2. `POST /api/posts/` 에 해당 `image_url` 포함해서 생성
3. `GET /uploads/{filename}` (백엔드 origin, `/api` prefix 아님) → 200, `Content-Type: image/*`
4. 프론트 검증: 브라우저가 `<img>` 렌더링 시 `VITE_API_BASE_URL` + `image_url`로 절대경로를 만드는지 (과거 상대경로로 인해 프론트 origin에 요청되어 깨졌던 회귀 케이스 — `PostEditView.vue`/`PostDetailView.vue`의 `resolvedImageUrl`)

### IT-03. 장소별 게시판 필터링 (location_id)
1. 실제 seed된 location id 하나 확보 (`GET /api/locations/?limit=1`)
2. 해당 `location_id`로 게시글 A 생성, 다른(또는 없는) `location_id`로 게시글 B 생성
3. `GET /api/posts/?location_id={A의 id}` → A만 반환, B 미포함
4. `GET /api/posts/` (필터 없음) → A, B 둘 다 포함

### IT-04. 프론트 라우팅 ↔ 백엔드 연동 (수동/E2E 브라우저 테스트 권장)
1. `/` (지도) 진입 → 지도 마커 또는 좌측 장소 목록 클릭
2. `/locations/{id}/posts` 로 라우팅되는지, 헤더에 장소명/카테고리/주소가 실제 데이터로 채워지는지
3. `+ 글쓰기` → `/locations/{id}/posts/new` → 작성 → 등록 모달에서 닉네임/비밀번호 입력 → 제출
4. 목록에 새 글 노출 확인 (해당 location_id로 필터된 상태)
5. 글 클릭 → 상세 진입 → 댓글 작성 → 목록 갱신 확인
6. 수정/삭제 버튼 → 비밀번호 오류/정상 케이스 각각 확인
7. `실시간 채팅` 탭 클릭 → "준비 중" 플레이스홀더 노출 확인 (미구현 기능이 사용자에게 명확히 안내되는지)

### IT-05. 장소 목록/지도 연동
1. `GET /api/locations/` bounds 파라미터로 지도 뷰포트 이동 시 재조회되는지 (`mapStore.fetchLocations`)
2. 무한 스크롤: `PlaceListPanel.vue`에서 스크롤 하단 도달 시 `fetchMoreLocations` 호출 및 중복 없이 추가 로드되는지
3. 카테고리별 마커 색상이 `style.css`의 `--cat-*` 토큰과 일치하는지 (관광지/음식점/문화시설/쇼핑/숙박)

### IT-06. AI 챗봇 (실키 필요, CI에서는 mock 권장)
1. 플로팅 위젯 열기 → 질문 전송 → 응답 렌더링 및 히스토리 유지
2. 연속 질문 시 이전 대화가 `history`로 함께 전송되는지 (Network 탭 확인)
3. `OPENAI_API_KEY` 미설정/잘못된 키 상태에서 502 처리 및 프론트 에러 UI 확인

### IT-07. CORS / 배포 설정
1. `settings.cors_origins_list`에 없는 origin에서 요청 시 브라우저에서 CORS 차단되는지
2. Netlify 배포본에서 `public/_redirects` (`/* /index.html 200`) 존재로 새로고침 시 404 안 나는지
3. Render 재배포 후 `backend/uploads/` 휘발 여부 확인 (경고 문서화 항목, 실패를 "예상된 제약"으로 기록)

---

## 3. 알려진 갭 (테스트보다 먼저 확인할 것)

| 항목 | 상태 |
|---|---|
| WebSocket 실시간 익명 채팅 (feature.md §5.4) | 백엔드 미구현 (`websocket_manager.py` 비어있음), 프론트는 "준비 중" placeholder만 존재 |
| `frontend/src/components/board/PostCard.vue`, `CommentItem.vue` | 라우터/페이지 어디서도 import되지 않는 미사용 컴포넌트로 보임 — 테스트 대상에서 제외하거나 실제 사용 여부 재확인 필요 |
| `frontend/src/components/chat/ChatBotWidget.vue`, `PlaceChatPanel.vue` | 위와 동일, `ChatWidget.vue`(실제 사용 중)와 별개로 존재 — 정리 필요 여부 확인 |
| `backend/app/services/chat_service.py`, `seed_service.py` | 빈 파일 (실제 로직은 `services/chat.py`, `scripts/seed.py`에 있음) |

---

## 부록. 외부 앱(다른 AI/테스트 도구)에 붙여넣을 프로젝트 요약

> **프로젝트**: SSAFIPLE — 서울 권역 지역 정보 공유 커뮤니티 & AI 여행 비서
> **스택**: Frontend Vue 3(Vite, Pinia, vue-router) / Backend FastAPI(Python, SQLAlchemy) / DB SQLite(`backend/localhub.db`) / 배포 Netlify+Render
> **인증**: 없음. 전 기능 익명. 게시판만 평문 비밀번호로 작성자 본인확인(의도된 설계, 교육 목적).
> **API 규칙**: 모든 REST 엔드포인트는 `/api` prefix 하위 (`/api/posts`, `/api/comments`, `/api/locations`, `/api/chat`). 정적 업로드 파일은 예외로 `/uploads/...` (prefix 없음).
> **핵심 도메인 3개**:
> 1. 지도/장소 — Kakao Maps SDK, `locations` 테이블(공공데이터 TourAPI 기반, 서울 좌표 검증됨), bounds/limit 기반 조회.
> 2. 커뮤니티 게시판 — `posts`/`comments` 테이블, 소프트 딜리트(`is_deleted`) + 게시글 삭제 시 댓글 CASCADE, 최근 장소별 게시판(`location_id`)으로 구조 변경됨(전역 게시판 라우트는 제거되고 `/locations/:location_id/posts`만 존재).
> 3. AI 챗봇 & 실시간 채팅 — `/api/chat`(OpenAI 연동, 대화 히스토리 유지, 비용 통제로 히스토리 턴수 제한)은 구현됨. 장소별 WebSocket 실시간 익명 채팅은 **미구현**(UI 플레이스홀더만 존재).
> **테스트 실행 방법**: 백엔드 `cd backend && python -m unittest discover -s tests -v`. 프론트는 자동화 테스트 러너 없음(수동/E2E 위주, Playwright 등 미설치).
> **주의사항**: 로컬 SQLite 파일 스키마가 최신 모델과 어긋나면(예: 컬럼 추가 후 마이그레이션 누락) 500 에러가 나므로, 스키마 변경 시 `ALTER TABLE`로 기존 로컬 DB를 맞춰야 함(자동 마이그레이션 없음, `create_all`은 신규 테이블만 생성).
