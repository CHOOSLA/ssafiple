# SSAFIPLE — AI 에이전트 지침서

서울 권역 지역 정보 공유 커뮤니티 & AI 여행 비서. 납기: **2026-07-16(목) 15:00 KST**. 개발 착수 이후 기능 요구사항 변경 불가 (기능명세서 v1.2가 baseline).

상세 규정은 아래 "문서 인덱스"에서 필요한 문서만 읽으세요. 이 파일은 항상 로드되므로 최소한으로 유지합니다.

## 항상 지켜야 할 핵심 규칙
* `.env`에 있는 API 키/DB 경로 등 민감정보를 코드나 커밋에 노출하지 않습니다.
* 게시판 비밀번호는 **의도적으로 평문 저장/비교**합니다 (교육 목적 명세). 이 예외는 게시판 비밀번호에만 한정됩니다.
* 게시글/댓글 삭제는 물리적 `DELETE`가 아닌 `is_deleted = True` 소프트 딜리트이며, 게시글 삭제 시 댓글도 연쇄 처리합니다.
* 커밋 메시지 포맷: `<Type>(<Scope>) : <한글 설명>` (` ) : ` 공백 형태 유지), co-authored-by 추가 금지. 브랜치 없이 master에서 직접 작업하므로 도메인·기능·관심사 단위로 커밋을 잘게 나누고 작업 중 체크포인트마다 커밋합니다. 상세: [.claude/docs/git-style.md](.claude/docs/git-style.md)
* 프론트엔드 UI 작업 전에는 `design-reference` 스킬을 사용해 `docs/design_draft/`의 시안을 먼저 확인합니다. 임의로 새 디자인을 만들지 않습니다.
* 3인 도메인 분할 체제입니다. 특정 도메인(지도/게시판/AI·채팅) 작업을 맡을 때는 해당 서브에이전트(`.claude/agents/`)를 사용해 담당 파일 범위와 제약을 지킵니다.

## 문서 인덱스 (`.claude/docs/`)
| 문서 | 언제 참고 |
|---|---|
| [overview.md](.claude/docs/overview.md) | 일정, 제출 산출물 체크리스트 확인 시 |
| [security.md](.claude/docs/security.md) | 환경변수/민감정보 처리 관련 작업 시 |
| [stack.md](.claude/docs/stack.md) | 기술 스택, Netlify/Render 배포 설정 작업 시 |
| [database.md](.claude/docs/database.md) | DB 모델·시딩·소프트 딜리트·좌표 검증 작업 시 |
| [feature.md](.claude/docs/feature.md) | 게시판/챗봇/지도/실시간 채팅 기능 요구사항 확인 시 |
| [license.md](.claude/docs/license.md) | 공공데이터 출처 표기·라이선스 관련 작업 시 |
| [git-style.md](.claude/docs/git-style.md) | 커밋 메시지 작성 시 |
| [cooperation.md](.claude/docs/cooperation.md) | 팀 역할, 도메인 담당 파일 범위 확인 시 |

## 서브에이전트 (`.claude/agents/`)
`map-domain` (장소/지도), `board-domain` (게시판), `chat-domain` (AI 챗봇·실시간 채팅) — 도메인별 독점 파일과 제약을 담고 있습니다.

## 스킬 (`.claude/skills/`)
`design-reference` — UI 구현/수정 전 디자인 시안 확인 절차.

## 관련 프로젝트 문서 (레포 루트, on-demand)
* [docs/SCHEMA.md](docs/SCHEMA.md) — DB 테이블 컬럼 명세
* [docs/SOURCE.md](docs/SOURCE.md) — 데이터 출처/라이선스 원문
* [docs/COOPERATION.md](docs/COOPERATION.md) — 팀 협업 가이드 전문
