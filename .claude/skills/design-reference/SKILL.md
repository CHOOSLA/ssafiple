---
name: design-reference
description: Use before implementing or modifying any Vue frontend UI/screen in this project (SSAFIPLE). Loads the HTML design draft under docs/design_draft/ so layout, color, typography, spacing, and component shape follow the approved design instead of being invented ad hoc. Trigger on requests to build/edit a page, view, or component, or on mentions of "디자인", "시안", "화면 구현/수정".
---

# 디자인 참고 (Design Reference)

프론트엔드 UI를 구현하거나 수정할 때는 **반드시 `docs/design_draft/` 하위 HTML 시안 파일을 먼저 읽고**, 그 시안의 레이아웃·컬러·타이포그래피·간격·컴포넌트 형태를 기준으로 작업합니다. 임의로 새로운 디자인을 창작하지 않습니다.

## 작업 절차
1. UI 관련 작업 착수 전, `docs/design_draft/*.html` 파일을 검색하여 해당 화면의 시안이 있는지 확인합니다 (예: `docs/design_draft/LocalHub.dc.html`).
2. 시안이 있으면 해당 파일을 읽고 디자인 토큰(색상, 폰트, radius, shadow, spacing)과 컴포넌트 구조를 그대로 Vue 3 컴포넌트로 옮깁니다.
3. 시안에 없는 화면은 아래 디자인 토큰과 스타일 규칙을 확장 적용하여 일관성을 유지합니다.

## 주의
시안 HTML은 프로토타입 마크업(`<x-dc>`, `<sc-for>`, `<sc-if>`, `{{ }}` 바인딩 등)을 포함하므로 **그대로 복사하지 않습니다.** 디자인 사양(스타일 값과 구조)만 추출해 Vue SFC + 프로젝트 공통 스타일 체계(`style.css`)에 맞게 재구성합니다.

## 핵심 디자인 토큰 (`LocalHub.dc.html` 기준)
* Accent: `#f15b4c` (hover `#d8402f`)
* Background: `#eef0ea` / Surface: `#fff` / Muted: `#f4f2ee`
* Text: `#1c1b1a` (sub `#a8a49b`, placeholder `#b4b0a8`)
* Border: `#eceae6`
* 카테고리 마커 컬러: 관광지 `#f15b4c`, 음식점 `#ef8a3c`, 문화시설 `#3f8fd0`, 쇼핑 `#8a6fd6`, 숙박 `#5aa06a`
* Font: `Pretendard` (fallback: system sans-serif)

## 전체 레이아웃 구조
* 좌측 60%: 스플릿 패널 (장소 목록 카드, 장소 상세 탭(글/채팅 분리), 글쓰기 폼, 게시글 상세)
* 우측 40%: 지도 뷰포트 (드래그, 줌, 장소 핀 마커 및 커스텀 오버레이 말풍선)
* 글로벌 플로팅 위젯: 우측 하단 AI 여행 도우미 챗봇 팝업 창
