<template>
  <div class="app-layout">
    <!-- 좌측 60% 패널: 동적 라우팅 영역 (목록, 상세, 글쓰기 등) -->
    <div class="side-panel">
      <!-- 헤더 (로고, 검색바 등 공통 영역) -->
      <div class="panel-header">
        <div class="brand">
          <span class="logo-icon">L</span>
          <div>
            <div class="brand-title">SSAFIPLE</div>
            <div class="brand-subtitle">서울 여행 정보 커뮤니티</div>
          </div>
        </div>
      </div>
      
      <!-- 메인 뷰포트 영역 (RouterView) -->
      <div class="panel-body">
        <router-view />
      </div>
    </div>

    <!-- 우측 40% 패널: 지도 전역 배경 영역 -->
    <!-- 지도는 항상 우측 전체 혹은 배경에 깔리게 설정하고, KakaoMap 컴포넌트를 렌더링합니다 -->
    <div class="map-container">
      <KakaoMap />
    </div>

    <!-- 우측 하단 플로팅 챗봇 영역 -->
    <div class="chatbot-widget">
      <!-- 챗봇 UI 컴포넌트 렌더링 위치 (feat/chat-domain 에서 구현) -->
    </div>
  </div>
</template>

<script setup>
import KakaoMap from '@/components/map/KakaoMap.vue'
// 앱 전체의 공통 레이아웃 스캐폴딩
</script>

<style scoped>
.app-layout {
  position: fixed;
  inset: 0;
  overflow: hidden;
  display: flex;
}

.side-panel {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 60%;
  z-index: 20;
  display: flex;
  flex-direction: column;
  background: #fff;
  box-shadow: 2px 0 26px rgba(20,20,19,.16);
}

.panel-header {
  padding: 16px 18px;
  flex: none;
  border-bottom: 1px solid var(--border-color);
}

.brand {
  display: flex;
  align-items: center;
  gap: 9px;
}

.logo-icon {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 900;
  font-size: 16px;
}

.brand-title {
  font-weight: 800;
  font-size: 16px;
  line-height: 1;
}

.brand-subtitle {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 3px;
}

.panel-body {
  flex: 1;
  min-height: 0;
  background: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.map-container {
  position: absolute;
  inset: 0;
  background: var(--bg-color);
  z-index: 10;
}

.placeholder-map {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-muted);
}

.chatbot-widget {
  position: absolute;
  right: 24px;
  bottom: 24px;
  z-index: 40;
}
</style>
