# SSAFIPLE — Claude Code 진입점

모든 핵심 규칙과 제약사항은 프로젝트 루트의 **`AGENTS.md`**에 통합되어 있습니다. 반드시 먼저 읽으세요.

## Claude Code 전용 도구

### 서브에이전트 (`.claude/agents/`)
`map-domain` (장소/지도), `board-domain` (게시판), `chat-domain` (AI 챗봇·실시간 채팅) — 도메인별 독점 파일 범위와 제약을 담고 있습니다. 특정 도메인 작업 시 해당 에이전트를 사용하세요.

### 스킬 (`.claude/skills/`)
`design-reference` — UI 구현/수정 전 `docs/design_draft/` 시안 확인 절차.

### 문서 인덱스 (`.claude/docs/`)
| 문서 | 언제 참고 |
|---|---|
| [feature.md](.claude/docs/feature.md) | 기능 요구사항 상세 및 디자인 시안 스크린샷 참조 시 |
| [git-style.md](.claude/docs/git-style.md) | 커밋 메시지 작성 및 커밋 단위 원칙 확인 시 |
| [cooperation.md](.claude/docs/cooperation.md) | 팀 역할·도메인 분배·충돌 방지 원칙 확인 시 |

### 관련 프로젝트 문서 (레포 루트)
* [AGENTS.md](AGENTS.md) — 전체 규칙 마스터 문서 (모든 AI 에이전트 공통)
* [docs/COOPERATION.md](docs/COOPERATION.md) — 팀 협업 가이드 전문
* [docs/SCHEMA.md](docs/SCHEMA.md) — DB 테이블 컬럼 명세
* [docs/SOURCE.md](docs/SOURCE.md) — 데이터 출처/라이선스 원문
