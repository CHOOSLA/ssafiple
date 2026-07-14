<template>
  <div class="app-root" @mousemove="onDrag" @mouseup="stopDrag" @mouseleave="stopDrag">
    
    <!-- 우측 배경 (전체): 지도 영역 -->
    <div class="map-viewport">
      <KakaoMap />
    </div>

    <!-- 좌측 패널: 앱 라우터 뷰 -->
    <div class="left-panel" :style="{ width: panelWidth + 'px' }">
      <!-- 라우터 뷰 안에 PlaceListPanel 등이 렌더링 됨 -->
      <router-view />
      
      <!-- 패널 크기 조절 핸들 -->
      <div class="resizer" @mousedown.prevent="startDrag">
        <div class="resizer-handle"></div>
      </div>
    </div>

    <!-- 우측 하단 플로팅 챗봇 영역 -->
    <div class="chatbot-container">
      <!-- 추후 Chatbot 컴포넌트 추가 예정 -->
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import KakaoMap from '@/components/map/KakaoMap.vue'

// 기본 패널 너비를 내용물이 넉넉하게 보이도록 550px로 지정
const DEFAULT_WIDTH = 550
const MIN_WIDTH = 450
const MAX_WIDTH = 900

const panelWidth = ref(DEFAULT_WIDTH)
const isDragging = ref(false)

onMounted(() => {
  const savedWidth = localStorage.getItem('localhub_panel_width_v2')
  if (savedWidth) {
    const parsed = parseInt(savedWidth, 10)
    if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
      panelWidth.value = parsed
    }
  }
})

const startDrag = () => {
  isDragging.value = true
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none' // 드래그 시 텍스트 선택 방지
}

const onDrag = (e) => {
  if (!isDragging.value) return
  let newWidth = e.clientX
  if (newWidth < MIN_WIDTH) newWidth = MIN_WIDTH
  if (newWidth > MAX_WIDTH) newWidth = MAX_WIDTH
  panelWidth.value = newWidth
}

const stopDrag = () => {
  if (isDragging.value) {
    isDragging.value = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    localStorage.setItem('localhub_panel_width_v2', panelWidth.value)
  }
}
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
  /* width는 인라인 스타일로 동적 할당됨 */
  z-index: 20;
  display: flex;
  flex-direction: column;
  background: #fff;
  box-shadow: 2px 0 26px rgba(20, 20, 19, 0.16);
}

/* 크기 조절 핸들 영역 */
.resizer {
  position: absolute;
  right: -5px;
  top: 0;
  bottom: 0;
  width: 10px;
  cursor: col-resize;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resizer:hover .resizer-handle,
.resizer:active .resizer-handle {
  background-color: var(--accent, #f15b4c);
  width: 4px;
}

.resizer-handle {
  width: 2px;
  height: 40px;
  background-color: #d9d6cf;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.chatbot-container {
  position: absolute;
  right: 24px;
  bottom: 24px;
  z-index: 40;
}
</style>
