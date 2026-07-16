<template>
  <div
    class="category-filter"
    :class="{ 'is-collapsed': isCollapsed }"
    :style="{ left: left + 'px' }"
    role="group"
    :aria-label="$t('map.categoryFilterAria')"
  >
    <button
      type="button"
      class="cat-option cat-all"
      :class="{ active: !selected }"
      @click="handleSelect(null)"
    >
      {{ $t('map.categoryAll') }}
      <span v-if="isCollapsed && !selected" class="toggle-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
      </span>
    </button>

    <button
      v-for="cat in categories"
      :key="cat"
      type="button"
      class="cat-option"
      :class="{ active: selected === cat }"
      :style="optionStyle(cat)"
      @click="handleSelect(cat)"
    >
      {{ $t(`common.category.${cat}`) }}
      <span v-if="isCollapsed && selected === cat" class="toggle-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({
  // 현재 지도 뷰포트 기준 좌측 여백(px). 좌측 패널 너비를 따라 갱신됨.
  left: {
    type: Number,
    default: 566
  },
  selected: {
    type: String,
    default: null
  }
})
const emit = defineEmits(['select'])

const isCollapsed = ref(window.innerWidth <= 768)

const handleSelect = (cat) => {
  // 모바일 접힌 상태일 때 현재 액티브 버튼을 누르면 펼치기
  if (window.innerWidth <= 768 && isCollapsed.value) {
    isCollapsed.value = false
    return
  }
  
  emit('select', cat)
  
  // 모바일에서는 카테고리 선택 후 자동으로 다시 접음
  if (window.innerWidth <= 768) {
    isCollapsed.value = true
  }
}

const handleResize = () => {
  if (window.innerWidth > 768) {
    isCollapsed.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 카테고리별 컬러 매핑 (KakaoMap.vue / PlaceListPanel.vue와 동일한 디자인 명세 값)
const catColors = {
  '관광지': '#f15b4c',
  '문화시설': '#3f8fd0',
  '쇼핑': '#8a6fd6',
  '숙박': '#5aa06a',
  '레포츠': '#1abc9c',
  '축제공연행사': '#e0507a',
  '여행코스': '#c9a227'
}

const categories = Object.keys(catColors)

// hover 시 사용할 연한 배경색(rgba)을 미리 계산 — color-mix() 등 최신 CSS 함수 의존 없이 폭넓은 호환성 확보
const hexToRgba = (hex, alpha) => {
  const clean = hex.replace('#', '')
  const r = parseInt(clean.substring(0, 2), 16)
  const g = parseInt(clean.substring(2, 4), 16)
  const b = parseInt(clean.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const optionStyle = (cat) => {
  const color = catColors[cat] || '#f15b4c'
  return {
    '--cat-color': color,
    '--cat-soft': hexToRgba(color, 0.12)
  }
}
</script>

<style scoped>
.category-filter {
  position: absolute;
  top: 24px;
  z-index: 15; /* 좌측 패널(20)보다는 낮고, 지도 위 다른 플로팅 요소들과는 겹치지 않게 배치 */
  max-width: calc(100vw - 24px);
  overflow-x: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border-hairline);
  border-radius: 16px;
  padding: 6px;
  box-shadow: 0 4px 14px rgba(28, 27, 26, 0.12);
  font-family: 'Pretendard', sans-serif;
  max-width: calc(100vw - 48px);
  overflow-x: auto;
}

.cat-option {
  flex: none;
  border: none;
  background: transparent;
  color: #8a877f;
  font-size: 13px;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, color 0.15s ease;
}

.cat-option:hover {
  background: var(--surface-muted);
  color: #1c1b1a;
}

/* 카테고리별 옵션: 선택 시 해당 카테고리 색상 배경 + 흰 글씨 */
.cat-option[style] {
  color: var(--cat-color);
}

.cat-option[style]:hover {
  background: var(--cat-soft);
}

.cat-option[style].active,
.cat-option[style].active:hover {
  background: var(--cat-color);
  color: #fff;
}

/* "전체" 옵션: accent 색 사용 */
.cat-all {
  color: #f15b4c;
}

.cat-all:hover {
  background: rgba(241, 91, 76, 0.1);
}

.cat-all.active,
.cat-all.active:hover {
  background: #f15b4c;
  color: #fff;
}

.toggle-icon {
  margin-left: 4px;
  vertical-align: middle;
  display: inline-flex;
}

/* 모바일: 인라인 left(패널 너비 기준)가 100vw를 넘어 화면 밖으로 밀리므로 고정 배치로 무력화 */
@media (max-width: 768px) {
  .category-filter {
    left: 12px !important;
    right: 12px;
    top: 12px;
    max-width: none;
    flex-wrap: wrap; /* 펼쳐졌을 때 줄바꿈 허용 */
  }
  .category-filter.is-collapsed {
    right: auto; /* 접혔을 때 전체 너비를 차지하지 않음 */
    max-width: max-content;
  }
  .category-filter.is-collapsed .cat-option:not(.active) {
    display: none;
  }
}
</style>
