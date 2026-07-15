---
title: 기술 스택 및 배포 제약
---

## 기술 스택 Baseline
* **Frontend**: Vue.js 3 SPA (Vite 빌드 도구)
* **Backend**: FastAPI (Python 비동기 처리, REST API)
* **Database**: SQLite (파일 기반, `backend/localhub.db`)
* **Deployment**: Netlify (Frontend), Render (Backend)

## 배포 환경 제약
* **Netlify (FE)**: Vue SPA 라우팅 적용 후 새로고침 시 404 에러를 방지하기 위해 `public/_redirects` 파일에 `/* /index.html 200` 리다이렉트 설정을 반드시 포함합니다.
* **Render (BE)**: 무료 플랜의 휘발성 파일 시스템 특성상 `backend/uploads/`에 임시 업로드되는 파일(이미지 첨부 P2 기능)이 재배포/재시작 시 유실될 수 있습니다. README에 경고를 명시합니다.
