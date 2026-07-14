# SSAFIPLE Frontend

이 디렉토리는 SSAFIPLE (서울 권역 지역 정보 공유 커뮤니티)의 **클라이언트(Vue 3 SPA)** 소스코드를 포함하고 있습니다.

## 🛠️ 기술 스택
* **Framework**: Vue 3 (Composition API, `<script setup>`)
* **Build Tool**: Vite
* **State Management**: Pinia
* **Routing**: Vue Router
* **Styling**: Vanilla CSS (CSS Variables 기반 디자인 시스템 구현)

## 📂 디렉토리 구조
* `src/assets/`: 이미지 리소스 및 전역 CSS 토큰 (`main.css`)
* `src/components/`: 도메인별 기능 단위의 재사용 컴포넌트 (`map`, `board`, `chat`, `common`)
* `src/pages/`: 화면 전체를 구성하는 뷰(View) 컴포넌트 (`HomeView.vue`, `MapView.vue` 등)
* `src/router/`: 라우팅 설정 (`index.js`)
* `src/stores/`: 도메인별 전역 상태 관리 (`mapStore.js`, `boardStore.js` 등)
* `src/utils/`: 전역 공통 유틸리티 모듈 (전역 Axios 인터셉터 `api.js` 등)
* `public/`: 정적 서빙 파일 및 배포 라우팅 룰 (`_redirects`)

## 🎨 디자인 시스템 및 공통 스타일 가이드
우리는 AI 에이전트 간의 화면 구현 통일성을 보장하기 위해 `src/style.css`에 글로벌 클래스를 정의해 두었습니다.
* **미리보기**: 앱을 실행한 후 `http://localhost:5173/example` 경로에 접속하면, 우리가 사용할 메인 컬러, 카테고리 컬러, 기본 버튼(`btn-primary`), 입력 폼(`input-base`), 팝업 애니메이션 등을 시각적으로 확인하고 코드를 재사용할 수 있습니다.
* 구체적인 UI 디자인 초안은 루트 경로의 `docs/design_draft/` 문서를 참고하세요.

## ⚙️ 환경 변수 (.env)
루트 디렉토리의 `.env.example` 파일을 복사하여 `.env` 파일을 생성하고 다음 변수들을 채워야 합니다.
```env
# Kakao Maps JS SDK 연동을 위한 자바스크립트 키
VITE_KAKAO_MAP_KEY=your_kakao_map_javascript_key_here

# 백엔드 API 서버 주소
VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 실행 방법

### 1. 패키지 의존성 설치
의존성 충돌을 방지하기 위해 `package-lock.json` 에 정의된 버전으로 엄격하게 패키지를 설치합니다.
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```
기본적으로 `http://localhost:5173` 에서 HMR(Hot Module Replacement)이 적용된 개발 서버가 구동됩니다.
