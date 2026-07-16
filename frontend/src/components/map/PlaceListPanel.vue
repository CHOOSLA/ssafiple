<template>
  <div class="place-list-panel">
    
    <!-- 로고 및 검색 헤더 영역 (LocalHub 디자인 참조) -->
    <div class="header-section">
      <div class="header-top-row">
        <button type="button" class="brand-row brand-row-link" @click="goHome">
          <img class="brand-logo" src="/favicon.svg" :alt="$t('common.brand.logoAlt')" />
          <div class="brand-text">
            <div class="brand-title">{{ $t('common.brand.name') }}</div>
            <div class="brand-subtitle">{{ $t('common.brand.tagline') }}</div>
          </div>
        </button>
        <div class="header-actions">
          <button class="theme-toggle-btn" @click="toggleTheme" aria-label="Toggle Theme">
            <span v-if="isDark">🌙</span>
            <span v-else>☀️</span>
          </button>
          <LangSwitcher />
        </div>
      </div>
      <div class="search-row">
        <svg width="16" height="16" viewBox="0 0 16 16"><circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" style="color: var(--text-secondary);" stroke-width="2"/><line x1="10.8" y1="10.8" x2="15" y2="15" stroke="currentColor" style="color: var(--text-secondary);" stroke-width="2" stroke-linecap="round"/></svg>
        <input
          class="search-input"
          :placeholder="$t('map.searchPlaceholder')"
          v-model="mapStore.searchQuery"
          @keyup.enter="handleSearch"
        />
        <button
          v-if="mapStore.searchQuery"
          type="button"
          class="search-clear-btn"
          :aria-label="$t('common.clearSearchAria')"
          @click="clearSearch"
        >
          ×
        </button>
      </div>
    </div>

    <!-- 목록 영역 -->
    <div class="list-container">
      <i18n-t keypath="map.nearbySummary" tag="div" class="list-header">
        <template #count><span>{{ mapStore.locations.length }}</span></template>
      </i18n-t>

      <div class="list-body">
        <div v-if="mapStore.isLoading" class="loading">{{ $t('map.loadingLocations') }}</div>
        <!-- 줌 아웃 시(결과 0개)에도 깔끔하게 표시되도록 메시지 통일 -->
        <div v-else-if="mapStore.locations.length === 0" class="empty">
          {{ mapStore.isZoomOutTooMuch ? $t('map.zoomInMessage') : $t('map.noResultsMessage') }}
        </div>
        
        <button 
          v-else 
          type="button"
          v-for="loc in displayLocations" 
          :key="loc.id" 
          class="place-card"
          :class="{ 'selected-place': mapStore.selectedLocation?.id === loc.id }"
          @click="goToPosts(loc)"
        >
          <!-- 왼쪽 썸네일 공간 -->
          <span 
            class="place-thumb" 
            :style="loc.image_url ? { backgroundImage: `url(${loc.image_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : {}"
          >
            <span class="cat-badge" :style="{ backgroundColor: getCatColor(loc.category) }">{{ $t(`common.category.${loc.category || '기타'}`) }}</span>
            <span v-if="!loc.image_url" class="thumb-text">NO PHOTO</span>
          </span>

          <!-- 중앙 장소 정보 -->
          <span class="place-info">
            <span class="p-name">{{ locale === 'en' ? loc.name_en || loc.name : loc.name }}</span>
            <span class="p-addr">{{ locale === 'en' ? loc.address_en || loc.address : loc.address }}</span>
            <span class="p-posts">{{ $t('map.postCount', { count: loc.post_count || 0 }) }}</span>
          </span>

          <!-- 오른쪽 게시글 미리보기 (항상 2슬롯 고정) -->
          <span class="post-preview-area">
            <template v-for="(pv, idx) in previewSlots(loc)" :key="pv ? pv.id : `empty-${idx}`">
              <span v-if="pv" class="preview-card">
                <span class="pv-title">{{ pv.title }}</span>
                <span class="pv-snippet">{{ pv.snippet }}</span>
                <span class="pv-comments">{{ $t('map.commentCount', { count: pv.comment_count }) }}</span>
              </span>
              <span v-else class="empty-preview">{{ emptyPreviewText(loc) }}</span>
            </template>
          </span>
        </button>

        <!-- 무한 스크롤 관찰 요소 -->
        <div ref="observerTarget" class="observer-trigger">
          <span v-if="mapStore.isFetchingMore">{{ $t('map.loadingMore') }}</span>
          <span v-else-if="!mapStore.hasMore && mapStore.locations.length > 0">{{ $t('map.allLoaded') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMapStore } from '@/stores/mapStore'
import LangSwitcher from '@/components/common/LangSwitcher.vue'

const mapStore = useMapStore()
const router = useRouter()
const { t, locale } = useI18n()

const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')

const toggleTheme = () => {
  isDark.value = !isDark.value
  const newTheme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', newTheme)
  localStorage.setItem('theme', newTheme)
}

const catColors = {
  '관광지': '#f15b4c',
  '문화시설': '#3f8fd0',
  '쇼핑': '#8a6fd6',
  '숙박': '#5aa06a',
  '레포츠': '#1abc9c',
  '축제공연행사': '#e0507a',
  '여행코스': '#c9a227'
}

const getCatColor = (cat) => {
  return catColors[cat] || '#f15b4c'
}

// 선택된 장소가 리스트 내에 존재하면 맨 위로 끌어올리기 위한 computed 배열
const displayLocations = computed(() => {
  const locs = [...mapStore.locations]
  if (!mapStore.selectedLocation) return locs

  const targetId = mapStore.selectedLocation.id
  const idx = locs.findIndex(loc => loc.id === targetId)

  if (idx > -1) {
    const [selected] = locs.splice(idx, 1)
    locs.unshift(selected)
  }
  return locs
})

// 게시글 미리보기를 항상 2슬롯으로 고정 (실제 글 또는 null)
const previewSlots = (loc) => {
  const posts = loc.latest_posts || []
  return [0, 1].map((i) => posts[i] || null)
}

// 빈 슬롯에 표시할 안내 문구 (전체 무글 vs 한 개만 있는 경우 구분)
const emptyPreviewText = (loc) => {
  const count = (loc.latest_posts || []).length
  return count === 0 ? t('map.firstPostPrompt') : t('map.morePostsPrompt')
}

const handleSearch = () => {
  // 현재 선택된 카테고리 필터를 유지한 채로 검색
  mapStore.fetchLocations(mapStore.categoryFilter, mapStore.searchQuery)
}

const clearSearch = () => {
  mapStore.setSearchQuery('')
  handleSearch()
}

const goToPosts = (loc) => {
  mapStore.selectLocation(loc)
  router.push(`/locations/${loc.id}/posts`)
}

const goHome = () => {
  router.push('/')
}

const observerTarget = ref(null)
let observer = null

onMounted(() => {
  isDark.value = document.documentElement.getAttribute('data-theme') === 'dark'
  
  if (mapStore.locations.length === 0) {
    mapStore.fetchLocations()
  }
  
  // 무한 스크롤 옵저버 설정
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && mapStore.hasMore && !mapStore.isFetchingMore && !mapStore.isLoading) {
      mapStore.fetchMoreLocations()
    }
  }, { threshold: 0.5 })
  
  if (observerTarget.value) {
    observer.observe(observerTarget.value)
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.place-list-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--surface);
  font-family: 'Pretendard', sans-serif;
}

/* 헤더 영역 */
.header-section {
  padding: 16px 18px;
  flex: none;
  border-bottom: 1px solid var(--border-hairline);
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-toggle-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.theme-toggle-btn:hover {
  background-color: var(--surface-hover);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}

.brand-row-link {
  border: none;
  background: none;
  padding: 0;
  text-align: left;
  cursor: pointer;
}

.brand-logo {
  width: 28px;
  height: 28px;
  display: block;
}

.brand-title {
  font-weight: 800;
  font-size: 16px;
  line-height: 1;
  color: var(--text-primary);
}

.brand-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 3px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface-muted);
  border-radius: 11px;
  padding: 10px 12px;
  margin-top: 13px;
}

.search-input {
  border: none;
  background: none;
  outline: none;
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
  min-width: 0;
}

.search-clear-btn {
  flex: none;
  width: 18px;
  height: 18px;
  border: none;
  border-radius: 50%;
  background: var(--border-input);
  color: #fff;
  font-size: 13px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.search-clear-btn:hover {
  background: var(--text-muted);
}

/* 리스트 컨테이너 */
.list-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  padding: 14px 16px 10px;
  flex: none;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-secondary);
}

.list-header span {
  color: var(--text-primary);
  font-weight: 700;
}

.list-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 장소 카드 디자인 (LocalHub 원본 스타일 복구) */
.place-card {
  container-type: inline-size; /* 컨테이너 쿼리 적용을 위한 선언 */
  display: flex;
  gap: 14px;
  width: 100%;
  min-width: 0;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid var(--border-color);
  padding: 18px;
  cursor: pointer;
  align-items: stretch;
  box-sizing: border-box;
  transition: background 0.2s;
}

.place-card:hover {
  background: var(--surface-hover);
}

.selected-place {
  background: var(--surface-sunken) !important;
  border-left: 4px solid var(--accent) !important;
  padding-left: 14px; /* border-left가 추가된 만큼 패딩 보정 */
}

/* 썸네일 영역 */
.place-thumb {
  width: 132px;
  height: 132px;
  flex: none;
  border-radius: 13px;
  background: repeating-linear-gradient(45deg, var(--surface-muted), var(--surface-muted) 9px, var(--surface-sunken) 9px, var(--surface-sunken) 18px);
  border: 1px solid var(--border-hairline);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.cat-badge {
  position: absolute;
  top: 9px;
  left: 9px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  padding: 3px 9px;
  border-radius: 16px;
}

.thumb-text {
  margin-bottom: 10px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

/* 장소 정보 영역 */
.place-info {
  /* 장소명·주소가 주 정보이므로 남는 폭을 갖고, 미리보기는 고정폭으로 양보
     (150px 고정 시 넓은 패널에서도 제목·주소가 2~3줄로 과도하게 개행됨) */
  flex: 1 1 auto;
  min-width: 150px;
  display: flex;
  flex-direction: column;
}

.p-name {
  font-weight: 800;
  font-size: 17px;
  color: var(--text-primary);
}

.p-addr {
  display: block;
  font-size: 12.5px;
  color: var(--text-secondary);
  margin-top: 7px;
  line-height: 1.45;
}

.p-posts {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: auto;
}

/* 게시글 미리보기 영역 */
.post-preview-area {
  flex: 0 0 190px;
  min-width: 0;
  display: flex;
  gap: 10px;
  overflow: hidden;
}

.empty-preview {
  flex: 1;
  min-width: 0;
  height: 132px;
  border: 1px dashed var(--border-input);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12.5px;
  color: var(--text-muted);
  text-align: center;
  padding: 0 10px;
}

/* 게시글 미리보기 카드 */
.preview-card {
  flex: 1 1 0;
  min-width: 0;
  height: 132px;
  border: 1px solid var(--border-hairline);
  border-radius: 12px;
  padding: 12px 13px;
  display: flex;
  flex-direction: column;
  background: var(--surface-card);
  overflow: hidden;
}

.pv-title {
  font-weight: 700;
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pv-snippet {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 7px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pv-comments {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: auto;
}

/* 컨테이너 쿼리: 패널(카드) 너비가 줄어들 때 반응형 처리 */
@container (max-width: 550px) {
  /* 카드가 550px 이하로 좁아지면 두 번째 미리보기 슬롯을 숨김 (1개만 표시) */
  .post-preview-area > span:nth-child(2) {
    display: none;
  }
}

@container (max-width: 420px) {
  /* 카드가 420px 이하로 아주 좁아지면 미리보기 영역 전체를 숨김 */
  .post-preview-area {
    display: none;
  }
}

.loading, .empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 무한 스크롤 관찰 타겟 */
.observer-trigger {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
