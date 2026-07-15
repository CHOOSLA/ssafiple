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
.app-root {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: linear-gradient(135deg, var(--bg-color, #eef0ea), #f4f1ea);
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
  background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(243,239,232,0.95));
  box-shadow: 2px 0 26px rgba(20, 20, 19, 0.16);
  overflow-y: auto;
}

/* 크기 조절 핸들 영역 */
.resizer {
  position: absolute;
  right: -6px;
  top: 0;
  bottom: 0;
  width: 12px;
  cursor: col-resize;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resizer-handle {
  width: 4px;
  height: 48px;
  background-color: #d1cfc8; /* 기본적으로 잘 보이도록 명도 조절 */
  border-radius: 4px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 핸들 내부에 그립(점 3개)을 그려서 드래그 가능함을 직관적으로 표시 */
.resizer-handle::after {
  content: "⋮";
  color: #fff;
  font-size: 14px;
  line-height: 1;
  font-weight: 900;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.resizer:hover .resizer-handle,
.resizer:active .resizer-handle {
  background-color: var(--accent, #f15b4c);
  transform: scaleY(1.1);
}

.chatbot-container {
  position: absolute;
  right: 24px;
  bottom: 24px;
  z-index: 40;
}
</style>
