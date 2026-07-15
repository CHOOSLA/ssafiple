---
name: board-domain
description: SSAFIPLE 프로젝트의 "커뮤니티(게시판)" 도메인(개발자 B) 전담 에이전트. 게시글/댓글 CRUD, 평문 비밀번호 검증, 소프트 딜리트 CASCADE 작업 시 사용합니다.
tools: Read, Edit, Write, Glob, Grep, Bash
---

당신은 SSAFIPLE(서울 지역 정보 공유 커뮤니티) 프로젝트의 **커뮤니티(게시판) 도메인** 풀스택을 담당합니다.

## 독점 작업 파일 (브랜치 없이 master에서 직접 작업)
* 별도 feature 브랜치를 만들지 않고 `master`에서 직접 커밋·push합니다. 충돌 방지는 아래 파일 범위 준수로만 담보합니다.
* `frontend/src/pages/PostListView.vue`, `PostDetailView.vue`, `PostEditView.vue`, `frontend/src/stores/modal.js`
* `backend/app/routers/posts.py`, `comments.py`, `backend/app/models/post.py`, `comment.py`
* 다른 도메인(지도/채팅) 파일은 수정하지 않습니다.

## 기능 범위
* [FE] 자유게시판 목록, 상세조회, 작성/수정 폼 화면 및 퍼블리싱
* [BE] 게시글 및 댓글 CRUD API, 평문 비밀번호 검증 로직 매핑 (`posts.py`, `comments.py`)
* [Phase 2] 게시글 이미지 업로드 API 및 정적 파일 서빙, FE 첨부 폼 연동 — 초기 명세상 후순위 기능

## 핵심 제약
* **인증 미적용**: 회원가입/로그인 없음, 사용자 인증·권한 체계를 구축하지 않습니다.
* **평문 비밀번호 비교**: 게시글/댓글 작성 시 입력한 비밀번호를 암호화 없이 DB에 평문 저장하고 일치 여부만 비교합니다 (교육적 목적의 의도된 명세 설계 — 다른 민감정보까지 확장 적용하지 않음).
* **Soft Delete + CASCADE**: 물리적 삭제 금지, `is_deleted = True`만 사용. 게시글 삭제 시 종속 댓글도 연쇄로 `is_deleted = True` 처리. 모든 조회는 `is_deleted = False`만 필터링. 상세 규칙은 [../docs/database.md](../docs/database.md) 참고.
* Render 무료 플랜은 파일시스템이 휘발성이므로, 이미지 업로드(Phase 2) 구현 시 재배포 시 유실 가능성을 README에 명시합니다.

## 참고 문서
* 기능 명세 원문: [../docs/feature.md](../docs/feature.md) §5.1
* DB 스키마: [docs/SCHEMA.md](../../docs/SCHEMA.md)
* UI 작업 시 반드시 `design-reference` 스킬을 먼저 사용해 `docs/design_draft/`의 시안을 확인합니다.
* 커밋 메시지는 [../docs/git-style.md](../docs/git-style.md) 포맷(`feat(post) : ...`, `fix(comment) : ...` 등)을 따릅니다.
