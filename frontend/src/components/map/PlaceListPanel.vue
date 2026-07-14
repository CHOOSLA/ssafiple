<template>
  <div class="place-list-panel">
    <!-- 검색 영역 -->
    <div class="search-section">
      <div class="input-wrapper">
        <input 
          type="text" 
          class="input-base" 
          placeholder="장소, 주소 검색" 
          v-model="searchQuery"
          @keyup.enter="handleSearch"
        />
      </div>
      <div class="filter-group">
        <button 
          v-for="cat in categories" 
          :key="cat"
          :class="['btn-outline', { active: selectedCategory === cat }]"
          @click="toggleCategory(cat)"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- 목록 영역 -->
    <div class="list-section">
      <div v-if="mapStore.isLoading" class="loading">데이터를 불러오는 중입니다...</div>
      <div v-else-if="mapStore.locations.length === 0" class="empty">검색 결과가 없습니다.</div>
      <div 
        v-else 
        v-for="loc in mapStore.locations" 
        :key="loc.id" 
        class="place-card"
        @click="mapStore.selectLocation(loc)"
      >
        <div class="place-info">
          <h3>{{ loc.name }}</h3>
          <span class="category-badge">{{ loc.category || '기타' }}</span>
        </div>
        <p class="address">{{ loc.address }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()
const searchQuery = ref('')
const selectedCategory = ref(null)

const categories = ['관광지', '음식점', '문화시설', '쇼핑', '숙박']

const handleSearch = () => {
  mapStore.fetchLocations(selectedCategory.value, searchQuery.value)
}

const toggleCategory = (cat) => {
  if (selectedCategory.value === cat) {
    selectedCategory.value = null // 해제
  } else {
    selectedCategory.value = cat
  }
  handleSearch()
}

onMounted(() => {
  // 초기 데이터 로드 (전체 혹은 제한된 개수)
  mapStore.fetchLocations()
})
</script>

<style scoped>
.place-list-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.search-section {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  background: #fff;
}

.filter-group {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.filter-group .btn-outline.active {
  background: var(--text-primary);
  color: #fff;
  border-color: var(--text-primary);
}

.list-section {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fdfdfc;
}

.loading, .empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-muted);
}

.place-card {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.place-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-color: #e3e0d9;
}

.place-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.place-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.category-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background: #f4f2ee;
  color: var(--text-secondary);
}

.address {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
