---
title: 기능적 요구사항 및 제약
---

## 5. 기능적 요구사항 및 제약

### 5.1. 익명 커뮤니티 (CRUD)
* 참조 시안 스크린샷: [create-post.png](../../docs/design_draft/screenshots/create-post.png) (글쓰기 폼), [post-items.png](../../docs/design_draft/screenshots/post-items.png) (게시글 목록/미리보기 카드)
* **인증 미적용**: 회원가입 및 로그인 기능이 없으며, 사용자 인증/권한 체계를 구축하지 않습니다.
* **평문 비밀번호 비교**: 게시글/댓글 작성 시 사용자가 입력한 **비밀번호를 암호화 없이 데이터베이스에 평문(Plaintext)으로 저장하고 일치 여부만 비교**합니다 (교육적 목적의 의도된 명세 설계).

### 5.2. AI 챗봇 기능 (FastAPI /api/chat)
* 참조 시안 스크린샷: [ai-chat.png](../../docs/design_draft/screenshots/ai-chat.png)
* **대화 기능 및 UI 구현**:
  * 대화 히스토리 유지, 모바일 스크롤 지원 및 우측 하단 플로팅 UI 컴포넌트를 구성합니다.
* **비용 통제 및 컨텍스트 제공 (CHT-01)**:
  * ⚠️ **[추후 구현 예정]** 유저의 자연어 질의에 따라 DB(locations, posts) 검색 결과를 우선 조회하여 컨텍스트로 결합하는 CHT-01 세부 최적화 로직은 뼈대 구축 완료 후 추후 단계에서 연동을 구현합니다.

### 5.3. 지도 시각화 (선택 기능)
* 참조 시안 스크린샷: [home.png](../../docs/design_draft/screenshots/home.png) (기본 진입 화면 — 좌측 장소 목록 + 우측 지도가 함께 보이는 뷰)
* **Kakao Maps JS SDK** 사용.
* 클라이언트 사이드 코드(브라우저)에 노출되는 Kakao Maps API 키 남용을 방지하기 위해, 카카오 개발자 콘솔의 **Web 플랫폼 도메인 등록(localhost 및 Netlify 배포 도메인)**을 설정합니다. 이 노출 특성과 보호 방식을 README에 반드시 기재합니다.
* 대용량 장소 표시로 인한 성능 저하를 막기 위해 전체 데이터를 일괄 응답하는 것을 금지하며, limit(기본 500개) 혹은 Bounds 기반 필터 조회를 구현해야 합니다.

### 5.4. 장소별 실시간 익명 채팅 (WebSocket)
* 참조 시안 스크린샷: [live-chat.png](../../docs/design_draft/screenshots/live-chat.png)
* 핵심 기능 중 하나로, 장소 상세 화면에서 글(게시판)과 분리된 실시간 익명 채팅 탭을 제공합니다.
* [BE] FastAPI WebSocket 엔드포인트로 장소별 Pub/Sub 채널 서버 파이프라인을 구성합니다.
* [FE] 장소 상세 뷰 내 실시간 채팅창을 WebSocket으로 연동합니다.
* 인증 미적용 원칙(§5.1)에 따라 별도 로그인 없이 익명으로 참여합니다.
