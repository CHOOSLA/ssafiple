---
title: 팀 협업 규칙
---

3인 개발 체제, 도메인 단위(Vertical Slice) 풀스택 분배. 전체 협업 가이드는 [docs/COOPERATION.md](../../docs/COOPERATION.md) 참고 (디자인 토큰 분석, Base Setup, Git Workflow 포함).

> **브랜치 전략 미사용**: 별도 feature 브랜치를 만들지 않고 3인 모두 `master`에서 직접 작업 후 각자 push합니다. 충돌 방지는 브랜치 분리가 아닌 아래 **도메인별 독점 작업 파일** 원칙으로 담보합니다.

## 도메인 및 역할
* **장소/지도 도메인** (개발자 A) — 담당 에이전트: `.claude/agents/map-domain.md`
* **커뮤니티(게시판) 도메인** (개발자 B) — 담당 에이전트: `.claude/agents/board-domain.md`
* **AI 및 실시간 통신 도메인** (개발자 C) — 담당 에이전트: `.claude/agents/chat-domain.md`

## 충돌 방지 원칙
브랜치 분리 없이 `master`에서 동시에 작업하므로, 기능 단위 폴더 및 화면 파일 단위로 역할을 명확히 분리하여 서로의 파일을 건드리지 않는 것이 유일한 충돌 방지 수단입니다. 각 도메인의 독점 작업 파일 목록은 `docs/COOPERATION.md` 및 각 에이전트 정의 파일을 참고합니다. push 전에는 담당 파일 외 변경이 섞이지 않았는지 확인하고, 자주 작은 단위로 pull/push합니다.
