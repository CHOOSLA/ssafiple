<template>
  <div class="app-root" :style="{ '--sheet-height': sheetHeight + '%' }" @mousemove="onDrag" @mouseup="stopDrag" @mouseleave="stopDrag">

    <!-- 우측 배경 (전체): 지도 영역 -->
    <div class="map-viewport">
      <KakaoMap />
    </div>

    <!-- 좌측 패널: 앱 라우터 뷰 -->
    <div class="left-panel" :class="{ 'sheet-dragging': isSheetDragging }" :style="{ width: panelWidth + 'px' }">
      <!-- 모바일 바텀시트 그래버: 드래그로 시트 높이(30/60/90%) 조절 -->
      <!-- touchstart.prevent: 터치 후 브라우저가 합성하는 mousedown이 드래그를
           한 번 더 트리거해 탭이 두 단계씩 건너뛰는 것을 방지 -->
      <div class="sheet-grabber" @touchstart.prevent="startSheetDrag" @mousedown.prevent="startSheetDrag">
        <div class="sheet-grabber-bar"></div>
      </div>
      <!-- 라우터 뷰 안에 PlaceListPanel 등이 렌더링 됨 -->
      <router-view />
      
      <!-- 패널 크기 조절 핸들 -->
      <div class="resizer" @mousedown.prevent="startDrag">
        <div class="resizer-handle"></div>
      </div>
    </div>

    <!-- 우측 하단 플로팅 챗봇 영역 -->
    <div class="chatbot-container">
      <ChatWidget />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import KakaoMap from '@/components/map/KakaoMap.vue'
import ChatWidget from '@/components/ChatWidget.vue'

// 기본 패널 너비를 내용물이 넉넉하게 보이도록 550px로 지정
const DEFAULT_WIDTH = 550
const MIN_WIDTH = 450
const MAX_WIDTH = 900

const panelWidth = ref(DEFAULT_WIDTH)
const isDragging = ref(false)

// 모바일 바텀시트 높이(vh %). 그래버 드래그 후 가까운 스냅 지점에 정착
const SHEET_SNAPS = [30, 60, 90]
const sheetHeight = ref(60)
const isSheetDragging = ref(false)

let sheetDragStartY = null
let sheetDragMoved = false

const onSheetDrag = (e) => {
  if (!isSheetDragging.value) return
  const y = e.touches ? e.touches[0].clientY : e.clientY
  if (sheetDragStartY !== null && Math.abs(y - sheetDragStartY) > 6) {
    sheetDragMoved = true
  }
  const pct = ((window.innerHeight - y) / window.innerHeight) * 100
  sheetHeight.value = Math.min(92, Math.max(15, pct))
}

const startSheetDrag = (e) => {
  isSheetDragging.value = true
  sheetDragStartY = e.touches ? e.touches[0].clientY : e.clientY
  sheetDragMoved = false
}

const stopSheetDrag = () => {
  if (!isSheetDragging.value) return
  isSheetDragging.value = false

  let next
  if (!sheetDragMoved) {
    // 드래그 없이 탭만 한 경우: 다음 스냅 단계로 순환 (30 → 60 → 90 → 30)
    const idx = SHEET_SNAPS.indexOf(
      SHEET_SNAPS.reduce((a, b) =>
        Math.abs(b - sheetHeight.value) < Math.abs(a - sheetHeight.value) ? b : a
      )
    )
    next = SHEET_SNAPS[(idx + 1) % SHEET_SNAPS.length]
  } else {
    next = SHEET_SNAPS.reduce((a, b) =>
      Math.abs(b - sheetHeight.value) < Math.abs(a - sheetHeight.value) ? b : a
    )
  }
  sheetHeight.value = next
  sheetDragStartY = null
  localStorage.setItem('localhub_sheet_height', String(next))
}

onMounted(() => {
  const savedWidth = localStorage.getItem('localhub_panel_width_v2')
  if (savedWidth) {
    const parsed = parseInt(savedWidth, 10)
    if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
      panelWidth.value = parsed
    }
  }

  const savedSheet = parseInt(localStorage.getItem('localhub_sheet_height') || '', 10)
  if (SHEET_SNAPS.includes(savedSheet)) {
    sheetHeight.value = savedSheet
  }

  // 그래버에 touch-action: none이 걸려 있어 시트 드래그 중 페이지 스크롤과 충돌하지 않음
  window.addEventListener('touchmove', onSheetDrag, { passive: true })
  window.addEventListener('touchend', stopSheetDrag)
  window.addEventListener('mousemove', onSheetDrag)
  window.addEventListener('mouseup', stopSheetDrag)
})

onUnmounted(() => {
  window.removeEventListener('touchmove', onSheetDrag)
  window.removeEventListener('touchend', stopSheetDrag)
  window.removeEventListener('mousemove', onSheetDrag)
  window.removeEventListener('mouseup', stopSheetDrag)
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
  background: var(--bg-color);
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
  background: var(--surface);
  box-shadow: 2px 0 26px rgba(0, 0, 0, 0.16);
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
  background-color: var(--text-muted);
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

/*
 * 모바일(≤768px): 좌/우 스플릿을 상/하 스플릿으로 전환.
 * 지도는 뷰포트 상단 40%에 그대로 남고, 좌측 패널이 하단 60% 시트로 내려온다.
 * 인라인으로 걸린 panelWidth(px)는 !important로 무력화 — 스크립트는 건드리지 않는다.
 */
/* 바텀시트 그래버는 데스크톱에서 숨김 */
.sheet-grabber {
  display: none;
}

@media (max-width: 768px) {
  .left-panel {
    width: 100% !important;
    top: auto;
    height: var(--sheet-height, 60%);
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    box-shadow: 0 -6px 26px rgba(20, 20, 19, 0.16);
    transition: height 0.25s ease;
  }

  /* 드래그 중에는 손가락을 즉각 따라가도록 스냅 애니메이션 해제 */
  .left-panel.sheet-dragging {
    transition: none;
  }

  /* 시트 상단 그래버: 드래그로 30/60/90% 조절, 탭하면 다음 단계로 전환.
     sticky로 스크롤에도 상단 고정. 스와이프가 목록 스크롤에 먹히지 않도록
     히트 영역을 전폭·두껍게 확보 */
  .sheet-grabber {
    display: flex;
    justify-content: center;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 60;
    min-height: 30px;
    padding: 8px 0;
    background: var(--surface);
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    touch-action: none;
    cursor: grab;
  }

  .sheet-grabber-bar {
    width: 56px;
    height: 6px;
    border-radius: 3px;
    background: var(--text-muted);
  }

  /* 너비 드래그 리사이저는 상하 레이아웃에서 의미가 없어 숨김 */
  .resizer {
    display: none;
  }

  /* 시트 높이를 따라 패널 입력창(댓글·채팅)과 겹치지 않게 함 */
  .chatbot-container {
    right: 16px;
    bottom: calc(var(--sheet-height, 60%) + 12px);
    transition: bottom 0.25s ease;
  }
}
</style>
