<template>
  <div
    class="category-filter"
    :style="{ left: left + 'px' }"
    role="group"
    :aria-label="$t('map.categoryFilterAria')"
  >
    <button
      type="button"
      class="cat-option cat-all"
      :class="{ active: !selected }"
      @click="$emit('select', null)"
    >
      {{ $t('map.categoryAll') }}
    </button>

    <button
      v-for="cat in categories"
      :key="cat"
      type="button"
      class="cat-option"
      :class="{ active: selected === cat }"
      :style="optionStyle(cat)"
      @click="$emit('select', cat)"
    >
      {{ $t(`common.category.${cat}`) }}
    </button>
  </div>
</template>

<script setup>
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
defineEmits(['select'])

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
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid #eceae6;
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
  background: #f4f2ee;
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
</style>
