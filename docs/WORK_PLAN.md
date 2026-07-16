# 병렬 작업 계획 (2026-07-16) — 모바일 · i18n 콘텐츠 · PWA · 다크테마

여러 Claude 인스턴스가 동시 작업하기 위한 **작업 분배와 인터페이스 계약** 문서입니다.
각 인스턴스는 자기 담당 섹션의 파일만 수정합니다. 계약을 임의로 바꾸지 않습니다.
계약 변경이 필요하면 작업을 멈추고 오케스트레이터(사용자)에게 보고합니다.

---

## 인스턴스 분배

| 인스턴스 | 담당 | 순서 |
|---|---|---|
| A | 전역 스타일 레이어: ① 모바일 반응형 → ② 다크테마 | 직렬 (① 커밋 후 ②) |
| B | ① PWA 설정 → ② UGC 번역 UI(게시글·댓글 "번역 보기") | ②는 A의 모바일 커밋 이후 시작 |
| C | i18n 콘텐츠 백엔드: 장소 배치 번역 + 번역 API + 채팅 규격 | 즉시 시작 |

공유 파일(`main.py`, `App.vue`, `router/index.js`, `style.css`, `models/`, `schemas/`)
수정이 자기 담당 범위를 넘으면 보고 후 진행합니다.

---

## A. 모바일 대응 → 다크테마

### A-1. 모바일 반응형
* 기준: 768px 이하에서 좌(목록/게시판) 60% + 우(지도) 40% 스플릿을 **상하 전환 또는 탭 전환**으로.
* 수정 범위: `frontend/src/style.css`, 각 컴포넌트 `<style>` 블록. **로직(script) 변경 금지.**
* 작업 중 발견하는 하드코딩 색상은 CSS 변수로 승격 (A-2 다크테마 대비).
* 참조: `docs/design_draft/` 시안, `.claude/skills/design-reference`.

### A-2. 다크테마 (A-1 커밋 후)
* `style.css`의 CSS 변수 체계에 `[data-theme="dark"]` 변수 세트 추가.
* 토글 버튼: 헤더 영역. 선택값 `localStorage` 저장, 초기값은 `prefers-color-scheme`.
* 카카오맵 타일은 다크 변환 불가 — 지도 영역은 라이트 유지하고 UI 크롬만 다크 처리.

## B. PWA → UGC 번역 UI

### B-1. PWA
* `vite-plugin-pwa` 도입: manifest(이름 SSAFIPLE, 테마색 `#f15b4c`, 배경 `#eef0ea`), 서비스워커(기본 프리캐시).
* 아이콘: `public/favicon.svg` 기반 192/512 PNG 생성 (`docs/logo/`에 기존 PNG 있음 — 재사용 가능).
* API 요청(`/api/*`)은 캐시하지 않음 (NetworkOnly). 수정 범위: `frontend/vite.config.js`, `frontend/public/`, `netlify.toml`.

### B-2. 게시글·댓글 "번역 보기" (A-1 커밋 후 시작)
* 게시글 상세·댓글에 "번역 보기 / 원문 보기" 토글 버튼.
* C가 만드는 `POST /api/translate` 사용 (계약은 §C-2). 응답 받으면 해당 텍스트만 교체 렌더.
* 수정 범위: `PostDetailView.vue`, `PostListView.vue`(미리보기는 선택), 관련 스토어.

## C. i18n 콘텐츠 백엔드 (계약 확정본)

### C-1. 장소 정적 데이터 — 배치 사전 번역
* `locations` 테이블에 `name_en`, `address_en` 컬럼 추가 (nullable).
* 배치 번역 스크립트 `backend/scripts/translate_locations.py`:
  OpenAI `gpt-4o-mini`로 6,482건 일괄 번역, 재실행 시 이미 번역된 행은 건너뜀(멱등).
* `GET /api/locations` 응답에 `name_en`, `address_en` 포함 — 프론트가 locale에 따라 표시 필드 선택.
* `docs/SCHEMA.md` 갱신 필수.

### C-2. UGC 온디맨드 번역 API
* `POST /api/translate` — 요청 `{"text": str, "target_lang": "en" | "ko"}`, 응답 `{"translated": str}`.
* 번역 결과 캐시: `translations` 테이블 `(id, source_hash UNIQUE(md5(text+target_lang)), translated_text, created_at)` — 같은 요청 재번역 방지.
* 모델: `gpt-4o-mini`. text 최대 2,000자 검증(422).

### C-3. 채팅 시스템 메시지 규격 변경 (서버 한국어 하드코딩 제거)
* 기존: `{"type": "system", "content": "OOO님이 입장했습니다."}`
* 변경: `{"type": "system", "event": "join" | "leave", "nickname": "익명 즐거운수달42"}`
  — 렌더 문구는 프론트 vue-i18n이 조립.
* 일반 메시지 · `self` 규격은 유지. 채팅 메시지 자체의 번역은 B-2와 동일하게 `POST /api/translate` 재사용(프론트 버튼은 후속 작업).
* **주의**: 이 규격 변경은 `PlaceChatPanel.vue`/`chatStore.js` 수정과 동시 배포 필요 — C가 백엔드 변경 후 프론트 반영까지 함께 커밋.

---

## 공통 규칙
1. 커밋은 자유, **push는 오케스트레이터 신호 후 한 인스턴스씩** (`git pull --rebase` 선행).
2. dev 서버 포트: A=5173/8000(대표), B·C는 검증 필요 시 5174/8001 사용.
3. `localhub.db` 스키마 변경·seed 재실행은 C만.
4. 완료 보고 형식: 변경 파일 목록 + 검증 방법(실행해 본 것) + 공유 파일 접촉 여부.
