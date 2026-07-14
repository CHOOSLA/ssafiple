<template>
  <div class="app-root">
    
    <!-- 우측 배경 (전체): 지도 영역 -->
    <div class="map-viewport">
      <KakaoMap />
    </div>

    <!-- 좌측 60% 패널: 앱 라우터 뷰 -->
    <div class="left-panel">
      <!-- 라우터 뷰 안에 PlaceListPanel 등이 렌더링 됨 -->
      <router-view />
    </div>

    <!-- 우측 하단 플로팅 챗봇 영역 -->
    <div class="chatbot-container">
      <!-- 추후 Chatbot 컴포넌트 추가 예정 -->
    </div>

  </div>
</template>

<script setup>
import KakaoMap from '@/components/map/KakaoMap.vue'
</script>

<style scoped>
/* LocalHub.dc.html 디자인 스펙 완벽 반영 */
.app-root {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: var(--bg-color, #eef0ea);
}

.map-viewport {
  position: absolute;
  inset: 0;
}

.left-panel {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 60%;
  z-index: 20;
  display: flex;
  flex-direction: column;
  background: #fff;
  box-shadow: 2px 0 26px rgba(20, 20, 19, 0.16);
}

.chatbot-container {
  position: absolute;
  right: 24px;
  bottom: 24px;
  z-index: 40;
}
</style>
