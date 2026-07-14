<template>
  <div class="example-container">
    <div class="header">
      <h1>🎨 디자인 시스템 & 공통 컴포넌트 (Example)</h1>
      <p>LocalHub 디자인 초안에서 추출한 공통 스타일과 컴포넌트 가이드입니다.</p>
    </div>

    <section class="section">
      <h2>1. 메인 컬러 테마 (Color Tokens)</h2>
      <div class="color-grid">
        <div class="color-card" style="background: var(--accent); color: white;">
          <span>--accent</span><span>#f15b4c</span>
        </div>
        <div class="color-card" style="background: var(--bg-color); color: #1c1b1a; border: 1px solid #ccc;">
          <span>--bg-color</span><span>#eef0ea</span>
        </div>
        <div class="color-card" style="background: var(--text-primary); color: white;">
          <span>--text-primary</span><span>#1c1b1a</span>
        </div>
        <div class="color-card" style="background: var(--text-secondary); color: white;">
          <span>--text-secondary</span><span>#8a877f</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>2. 카테고리 컬러 (Category Colors)</h2>
      <div class="color-grid">
        <div class="color-card cat-tour">관광지 (--cat-tour)</div>
        <div class="color-card cat-food">음식점 (--cat-food)</div>
        <div class="color-card cat-culture">문화시설 (--cat-culture)</div>
        <div class="color-card cat-shopping">쇼핑 (--cat-shopping)</div>
        <div class="color-card cat-stay">숙박 (--cat-stay)</div>
      </div>
    </section>

    <section class="section">
      <h2>3. 타이포그래피 (Typography)</h2>
      <div class="type-box">
        <h1>Heading 1 (24px, 800) - 서울 지역 관광지</h1>
        <h2>Heading 2 (20px, 700) - 게시글 제목 예시</h2>
        <p class="body-text">Body Text (14px, 400) - 본문 내용입니다. 기본 폰트는 Pretendard가 전역으로 적용되며, 가독성을 위한 최적화가 이루어져 있습니다. 긴 텍스트의 줄바꿈과 자간을 확인하세요.</p>
        <span class="caption-text">Caption (11px, 400, muted) - 부가 설명이나 날짜 등에 사용됩니다.</span>
      </div>
    </section>

    <section class="section">
      <h2>4. 공통 컴포넌트 (Components)</h2>
      
      <div class="component-group">
        <h3>Primary Buttons</h3>
        <div class="flex-row">
          <button class="btn-primary">기본 버튼</button>
          <button class="btn-primary btn-round">
            <span style="font-size: 16px; margin-right: 4px;">+</span>글쓰기
          </button>
          <button class="btn-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff"><polygon points="4,3 22,12 4,21 4,14 15,12 4,10"/></svg>
          </button>
        </div>
      </div>

      <div class="component-group">
        <h3>Secondary / Action Buttons</h3>
        <div class="flex-row">
          <button class="btn-secondary">취소</button>
          <button class="btn-outline">태그/필터 버튼</button>
          <button class="btn-circle-action">‹</button>
        </div>
      </div>

      <div class="component-group">
        <h3>Input & Forms</h3>
        <div class="flex-column">
          <div class="input-wrapper">
             <input type="text" class="input-base" placeholder="장소, 주소 검색" />
          </div>
          <div class="input-wrapper">
             <input type="text" class="input-rounded" placeholder="익명으로 채팅 보내기" />
          </div>
          <textarea class="textarea-base" placeholder="내용을 입력하세요. 로그인 없이 익명으로 등록됩니다."></textarea>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>5. 애니메이션 & 효과 (Animations)</h2>
      <div class="flex-row">
        <div class="anim-box anim-pop">
          팝업 애니메이션 (lh-pop)
        </div>
        <div class="anim-box anim-typing">
          <span></span><span></span><span></span>
          (lh-blink)
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.example-container {
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
  overflow-y: auto;
  height: 100%;
}

.header {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.header h1 { margin: 0 0 10px 0; font-size: 28px; font-weight: 800; }
.header p { margin: 0; color: var(--text-secondary); }

.section {
  margin-bottom: 48px;
}

.section h2 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text-primary);
}

/* Color Tokens */
.color-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.color-card {
  width: 140px;
  height: 80px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 13px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.color-card span { display: block; margin: 2px 0; }

.cat-tour { background: var(--cat-tour); color: white; }
.cat-food { background: var(--cat-food); color: white; }
.cat-culture { background: var(--cat-culture); color: white; }
.cat-shopping { background: var(--cat-shopping); color: white; }
.cat-stay { background: var(--cat-stay); color: white; }

/* Typography */
.type-box {
  background: white;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}
.type-box h1 { margin: 0 0 16px 0; font-size: 24px; font-weight: 800; }
.type-box h2 { margin: 0 0 16px 0; font-size: 20px; font-weight: 700; }
.body-text { margin: 0 0 16px 0; font-size: 14.5px; line-height: 1.6; }
.caption-text { display: block; font-size: 11px; color: var(--text-muted); }

/* Components */
.component-group {
  margin-bottom: 24px;
}
.component-group h3 {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.flex-row { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.flex-column { display: flex; flex-direction: column; gap: 12px; max-width: 400px; }

/* Buttons */
.btn-primary {
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 11px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}
.btn-primary:hover { filter: brightness(1.06); }

.btn-round {
  border-radius: 20px;
  padding: 10px 18px;
  box-shadow: 0 4px 12px rgba(241,91,76,.28);
}

.btn-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--accent);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary {
  background: #f2f1ed;
  border: none;
  border-radius: 11px;
  padding: 12px 24px;
  font-weight: 700;
  font-size: 14px;
  color: #6b6864;
  cursor: pointer;
}

.btn-outline {
  background: #f4f2ee;
  border: 1px solid #e8e5de;
  border-radius: 16px;
  padding: 8px 14px;
  font-size: 13px;
  color: #4a4843;
  cursor: pointer;
}

.btn-circle-action {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f4f2ee;
  border: none;
  cursor: pointer;
  font-size: 22px;
  line-height: 1;
  color: #1c1b1a;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Inputs */
.input-wrapper {
  background: #f4f2ee;
  border-radius: 11px;
  padding: 12px 16px;
}
.input-base {
  border: none;
  background: none;
  outline: none;
  width: 100%;
  font-size: 14.5px;
  color: var(--text-primary);
}

.input-rounded {
  border: 1px solid #e3e0d9;
  border-radius: 22px;
  padding: 12px 18px;
  font-size: 14px;
  outline: none;
  width: 100%;
  background: white;
}

.textarea-base {
  border: 1px solid var(--border-color);
  border-radius: 11px;
  outline: none;
  resize: none;
  height: 120px;
  padding: 16px;
  font-size: 14.5px;
  line-height: 1.6;
}

/* Animations */
.anim-box {
  width: 180px;
  height: 100px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: bold;
}
.anim-pop { animation: lh-pop 0.5s ease both; }
.anim-typing { gap: 6px; }
.anim-typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a8a49b;
  animation: lh-blink 1.2s infinite;
}
.anim-typing span:nth-child(2) { animation-delay: 0.2s; }
.anim-typing span:nth-child(3) { animation-delay: 0.4s; }
</style>
