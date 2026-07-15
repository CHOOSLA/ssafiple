<template>
  <div class="place-list-panel">
    
    <!-- 로고 및 검색 헤더 영역 (LocalHub 디자인 참조) -->
    <div class="header-section">
      <div class="brand-row">
        <span class="brand-logo">S</span>
        <div class="brand-text">
          <div class="brand-title">SSAFIPLE</div>
          <div class="brand-subtitle">서울 여행 정보 커뮤니티</div>
        </div>
      </div>
      <div class="search-row">
        <svg width="16" height="16" viewBox="0 0 16 16"><circle cx="7" cy="7" r="5" fill="none" stroke="#9a968f" stroke-width="2"/><line x1="10.8" y1="10.8" x2="15" y2="15" stroke="#9a968f" stroke-width="2" stroke-linecap="round"/></svg>
        <input
          class="search-input"
          placeholder="장소, 주소 검색"
          v-model="mapStore.searchQuery"
          @keyup.enter="handleSearch"
        />
      </div>
    </div>

    <!-- 목록 영역 -->
    <div class="list-container">
      <div class="list-header">주변 장소 <span>{{ mapStore.locations.length }}</span>곳 · 핀을 눌러 탐색하세요</div>
      
      <div class="list-body">
        <div v-if="mapStore.isLoading" class="loading">데이터를 불러오는 중입니다...</div>
        <div v-else-if="mapStore.locations.length === 0" class="empty">검색 결과가 없습니다.</div>
        
        <button 
          v-else 
          type="button"
          v-for="loc in mapStore.locations" 
          :key="loc.id" 
          class="place-card"
          @click="goToPosts(loc)"
        >
          <!-- 왼쪽 썸네일 공간 -->
          <span 
            class="place-thumb" 
            :style="loc.image_url ? { backgroundImage: `url(${loc.image_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : {}"
          >
            <span class="cat-badge" :style="{ backgroundColor: getCatColor(loc.category) }">{{ loc.category || '기타' }}</span>
            <span v-if="!loc.image_url" class="thumb-text">NO PHOTO</span>
          </span>

          <!-- 중앙 장소 정보 -->
          <span class="place-info">
            <span class="p-name">{{ loc.name }}</span>
            <span class="p-addr">{{ loc.address }}</span>
            <span class="p-posts">게시글 {{ loc.post_count || 0 }}개</span>
          </span>

          <!-- 오른쪽 게시글 미리보기 (항상 2슬롯 고정) -->
          <span class="post-preview-area">
            <template v-for="(pv, idx) in previewSlots(loc)" :key="pv ? pv.id : `empty-${idx}`">
              <span v-if="pv" class="preview-card">
                <span class="pv-title">{{ pv.title }}</span>
                <span class="pv-snippet">{{ pv.snippet }}</span>
                <span class="pv-comments">댓글 {{ pv.comment_count }}개</span>
              </span>
              <span v-else class="empty-preview">{{ emptyPreviewText(loc) }}</span>
            </template>
          </span>
        </button>
        
        <!-- 무한 스크롤 관찰 요소 -->
        <div ref="observerTarget" class="observer-trigger">
          <span v-if="mapStore.isFetchingMore">추가 데이터를 불러오는 중...</span>
          <span v-else-if="!mapStore.hasMore && mapStore.locations.length > 0">모든 장소를 불러왔습니다.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()
const router = useRouter()

const catColors = {
  '관광지': '#f15b4c',
  '음식점': '#ef8a3c',
  '문화시설': '#3f8fd0',
  '쇼핑': '#8a6fd6',
  '숙박': '#5aa06a'
}

const getCatColor = (cat) => {
  return catColors[cat] || '#f15b4c'
}

// 게시글 미리보기를 항상 2슬롯으로 고정 (실제 글 또는 null)
const previewSlots = (loc) => {
  const posts = loc.latest_posts || []
  return [0, 1].map((i) => posts[i] || null)
}

// 빈 슬롯에 표시할 안내 문구 (전체 무글 vs 한 개만 있는 경우 구분)
const emptyPreviewText = (loc) => {
  const count = (loc.latest_posts || []).length
  return count === 0 ? '첫 글을 남겨주세요' : '글을 더 남겨주세요'
}

const handleSearch = () => {
  mapStore.fetchLocations(null, mapStore.searchQuery)
}

const goToPosts = (loc) => {
  mapStore.selectLocation(loc)
  router.push(`/locations/${loc.id}/posts`)
}

const observerTarget = ref(null)
let observer = null

onMounted(() => {
  mapStore.fetchLocations()
  
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
  background: #fff;
  font-family: 'Pretendard', sans-serif;
}

/* 헤더 영역 */
.header-section {
  padding: 16px 18px;
  flex: none;
  border-bottom: 1px solid #eceae6;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.brand-logo {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: var(--accent, #f15b4c);
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
  color: #1c1b1a;
}

.brand-subtitle {
  font-size: 11px;
  color: #a8a49b;
  margin-top: 3px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f4f2ee;
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
  color: #1c1b1a;
  min-width: 0;
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
  border-bottom: 1px solid #f0eee9;
  font-size: 13px;
  color: #8a877f;
}

.list-header span {
  color: #1c1b1a;
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
  display: flex;
  gap: 14px;
  width: 100%;
  min-width: 0;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid #f0eee9;
  padding: 18px;
  cursor: pointer;
  align-items: stretch;
  box-sizing: border-box;
  transition: background 0.2s;
}

.place-card:hover {
  background: #faf9f6;
}

/* 썸네일 영역 */
.place-thumb {
  width: 132px;
  height: 132px;
  flex: none;
  border-radius: 13px;
  background: repeating-linear-gradient(45deg, #e9e7e0, #e9e7e0 9px, #f2f1ec 9px, #f2f1ec 18px);
  border: 1px solid #ece9e2;
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
  color: #aaa69d;
  letter-spacing: 0.04em;
}

/* 장소 정보 영역 */
.place-info {
  width: 150px;
  flex: none;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.p-name {
  font-weight: 800;
  font-size: 17px;
  color: #1c1b1a;
}

.p-addr {
  display: block;
  font-size: 12.5px;
  color: #8a877f;
  margin-top: 7px;
  line-height: 1.45;
}

.p-posts {
  display: block;
  font-size: 12px;
  color: #b0ada5;
  margin-top: auto;
}

/* 게시글 미리보기 영역 */
.post-preview-area {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  gap: 10px;
  overflow: hidden;
}

.empty-preview {
  flex: 1;
  min-width: 0;
  height: 132px;
  border: 1px dashed #e3e0d9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12.5px;
  color: #c2bfb7;
  text-align: center;
  padding: 0 10px;
}

/* 게시글 미리보기 카드 */
.preview-card {
  flex: 1 1 0;
  min-width: 0;
  height: 132px;
  border: 1px solid #eceae6;
  border-radius: 12px;
  padding: 12px 13px;
  display: flex;
  flex-direction: column;
  background: #fcfbf9;
  overflow: hidden;
}

.pv-title {
  font-weight: 700;
  font-size: 13px;
  line-height: 1.4;
  color: #1c1b1a;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pv-snippet {
  font-size: 12px;
  color: #8a877f;
  margin-top: 7px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pv-comments {
  font-size: 11px;
  color: #b0ada5;
  margin-top: auto;
}

.loading, .empty {
  text-align: center;
  padding: 40px 0;
  color: #8a877f;
  font-size: 14px;
}

/* 무한 스크롤 관찰 타겟 */
.observer-trigger {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #b0ada5;
}
</style>
