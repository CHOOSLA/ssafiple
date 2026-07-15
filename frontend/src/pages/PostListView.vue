<template>
  <div class="page-shell">
    <section class="app-shell">
      <header class="panel-header">
        <div class="brand-row">
          <img class="brand-badge" src="/favicon.svg" alt="SSAFIPLE 로고" />
          <div>
            <div class="brand-title">SSAFIPLE</div>
            <div class="brand-subtitle">서울 여행 정보 커뮤니티</div>
          </div>
        </div>
        <div class="search-bar">
          <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
            <circle cx="7" cy="7" r="5" fill="none" stroke="#9a968f" stroke-width="2" />
            <line x1="10.8" y1="10.8" x2="15" y2="15" stroke="#9a968f" stroke-width="2" stroke-linecap="round" />
          </svg>
          <input v-model="searchQuery" placeholder="게시글 제목/내용 검색" />
        </div>
      </header>

      <div class="place-hero">
        <button type="button" class="hero-back" @click="goBack">‹</button>
        <img v-if="placeImageUrl" :src="placeImageUrl" class="hero-photo" alt="" />
        <span v-else class="hero-placeholder">PHOTO · {{ placeName }}</span>
      </div>

      <div class="place-info-bar">
        <div class="place-name-row">
          <span class="place-name">{{ placeName }}</span>
          <span class="place-cat" :style="{ color: placeCategoryColor }">{{ placeCategory }}</span>
        </div>
        <div class="place-address">{{ placeAddress }}</div>
      </div>

      <div class="place-tabs">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'posts' }"
          @click="activeTab = 'posts'"
        >게시글 {{ filteredPosts.length }}</button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'chat' }"
          @click="activeTab = 'chat'"
        >실시간 채팅</button>
      </div>

      <template v-if="activeTab === 'posts'">
        <div class="list-toolbar">
          <router-link :to="`/locations/${$route.params.location_id}/posts/new`" class="write-btn"><span class="write-icon">+</span>글쓰기</router-link>
        </div>

        <div class="panel-body">
          <div v-if="loading" class="status-message">불러오는 중...</div>
          <div v-else-if="error" class="status-message error">{{ error }}</div>
          <div v-else class="post-list">
            <router-link v-for="post in filteredPosts" :key="post.id" :to="`/locations/${$route.params.location_id}/posts/${post.id}`" class="post-item">
              <span class="post-title">{{ post.title }}</span>
              <p class="post-preview">{{ post.content }}</p>
              <div class="post-meta">
                <span>{{ post.author }}</span>
                <span>{{ formatDate(post.created_at) }}</span>
                <span>댓글 {{ post.comments?.length || 0 }}</span>
              </div>
            </router-link>
            <div v-if="filteredPosts.length === 0" class="empty-row">
              <div class="empty-title">아직 등록된 게시글이 없어요.</div>
              <div class="empty-sub">첫 게시글을 남겨보세요.</div>
            </div>
          </div>
        </div>
      </template>

      <PlaceChatPanel v-else :location-id="route.params.location_id" />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMapStore } from '@/stores/mapStore'
import PlaceChatPanel from '@/components/chat/PlaceChatPanel.vue'
import api from '../api'

const router = useRouter()
const route = useRoute()
const mapStore = useMapStore()

const posts = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const activeTab = ref('posts')

// 스토어에서 선택된 장소 정보를 우선 표시하고, API로 받아온 상세 정보로 보강 (새로고침/직접 진입 대응)
const location = ref(null)

const placeName = computed(() => location.value?.name || mapStore.selectedLocation?.name || '전체 장소')
const placeCategory = computed(() => location.value?.category || mapStore.selectedLocation?.category || '')

// 지도 마커 색상(카테고리별)과 동일한 팔레트 (style.css --cat-* 토큰 기준)
const CATEGORY_COLORS = {
  '관광지': 'var(--cat-tour)',
  '음식점': 'var(--cat-food)',
  '문화시설': 'var(--cat-culture)',
  '쇼핑': 'var(--cat-shopping)',
  '숙박': 'var(--cat-stay)'
}
const placeCategoryColor = computed(() => CATEGORY_COLORS[placeCategory.value] || 'var(--cat-tour)')
const placeAddress = computed(() => location.value?.address || mapStore.selectedLocation?.address || '')

// 상대경로(/uploads/...)일 수 있으므로 백엔드 origin 기준으로 풀어줌
const placeImageUrl = computed(() => {
  const url = location.value?.image_url || mapStore.selectedLocation?.image_url
  if (!url) return ''
  if (/^https?:\/\//.test(url)) return url
  return `${import.meta.env.VITE_API_BASE_URL}${url}`
})

const fetchLocation = async () => {
  const locId = route.params.location_id
  if (!locId) return
  try {
    const { data } = await api.get(`/locations/${locId}`)
    location.value = data
  } catch (err) {
    // 장소 정보를 못 가져와도 게시판 자체는 계속 보여준다
  }
}

const goBack = () => {
  router.push('/')
}

const filteredPosts = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return posts.value

  return posts.value.filter((post) => {
    const target = `${post.title} ${post.content} ${post.author}`.toLowerCase()
    return target.includes(query)
  })
})

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('ko-KR')
}

const fetchPosts = async () => {
  loading.value = true
  error.value = ''
  try {
    // URL 동적 라우팅 패러미터에서 location_id 가져오기
    const locId = route.params.location_id
    const params = locId ? { location_id: locId } : {}
    
    const { data } = await api.get('/posts/', { params })
    posts.value = data
  } catch (err) {
    error.value = '게시글을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLocation()
  fetchPosts()
})

// 같은 라우트에서 location_id 파라미터만 바뀌면(지도에서 다른 핀 클릭 등)
// 컴포넌트가 재사용되어 onMounted가 다시 실행되지 않으므로, 파라미터를 감지해 데이터를 다시 불러온다
watch(
  () => route.params.location_id,
  (newId, oldId) => {
    if (!newId || newId === oldId) return
    location.value = null
    posts.value = []
    searchQuery.value = ''
    activeTab.value = 'posts'
    fetchLocation()
    fetchPosts()
  }
)
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  padding: 0;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 245, 239, 0.96));
}

.panel-header {
  padding: 16px 18px 12px;
  border-bottom: 1px solid #eceae6;
  flex: none;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.brand-badge {
  width: 28px;
  height: 28px;
  display: block;
}

.brand-title {
  font-weight: 800;
  font-size: 16px;
}

.brand-subtitle {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 3px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f4f2ee;
  border-radius: 11px;
  padding: 10px 12px;
  margin-top: 13px;
}

.search-bar input {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  min-width: 0;
  font-size: 14px;
  color: var(--text-primary);
}

.place-hero {
  position: relative;
  height: 200px;
  flex: none;
  background: repeating-linear-gradient(45deg, #e6e4dd, #e6e4dd 11px, #f0efea 11px, #f0efea 22px);
}

.hero-back {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.16);
  cursor: pointer;
  font-size: 22px;
  line-height: 1;
  color: var(--text-primary);
  padding: 0;
}

.hero-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 11px;
  color: #aaa69d;
  letter-spacing: 0.04em;
}

.place-info-bar {
  padding: 15px 16px 13px;
  flex: none;
  border-bottom: 1px solid #f0eee9;
}

.place-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.place-name {
  font-size: 21px;
  font-weight: 800;
  color: var(--text-primary);
}

.place-cat {
  font-size: 12px;
  font-weight: 700;
  background: #f6f5f2;
  padding: 3px 9px;
  border-radius: 20px;
}

.place-address {
  margin-top: 9px;
  color: #6b6864;
  font-size: 13.5px;
  line-height: 1.5;
}

.place-tabs {
  display: flex;
  border-bottom: 1px solid #eceae6;
  flex: none;
}

.tab-btn {
  flex: 1;
  padding: 13px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-muted);
  border-bottom: 2.5px solid transparent;
}

.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.list-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 11px 16px 8px;
  flex: none;
}

.write-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(241, 91, 76, 0.32);
}

.write-icon {
  font-size: 16px;
  line-height: 1;
}

.panel-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.post-list {
  display: flex;
  flex-direction: column;
}

.post-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-bottom: 1px solid #f4f2ee;
  padding: 15px 16px;
  cursor: pointer;
  color: inherit;
  transition: background-color 0.2s ease;
}

.post-item:hover {
  background: #faf9f6;
}

.post-title {
  display: block;
  font-weight: 700;
  font-size: 14.5px;
  line-height: 1.4;
  color: var(--text-primary);
}

.post-preview {
  display: block;
  margin: 5px 0 0;
  font-size: 13px;
  color: #6b6864;
  line-height: 1.55;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 11.5px;
  color: var(--text-muted);
  margin-top: 9px;
}

.status-message {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.status-message.error {
  color: #d24b3d;
}

.empty-row {
  padding: 52px 20px;
  text-align: center;
}

.empty-title {
  font-size: 14px;
  color: var(--text-secondary);
}

.empty-sub {
  font-size: 12.5px;
  color: var(--text-muted);
  margin-top: 6px;
}
</style>
