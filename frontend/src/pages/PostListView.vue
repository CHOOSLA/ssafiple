<template>
  <div class="page-shell">
    <section class="app-shell">
      <header class="panel-header">
        <div class="header-top-row">
          <button type="button" class="brand-row brand-row-link" @click="goBack">
            <img class="brand-badge" src="/favicon.svg" :alt="$t('common.brand.logoAlt')" />
            <div>
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
        <div class="search-bar">
          <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
            <circle cx="7" cy="7" r="5" fill="none" stroke="#9a968f" stroke-width="2" />
            <line x1="10.8" y1="10.8" x2="15" y2="15" stroke="#9a968f" stroke-width="2" stroke-linecap="round" />
          </svg>
          <input v-model="searchQuery" :placeholder="$t('board.searchPlaceholder')" />
          <button
            v-if="searchQuery"
            type="button"
            class="search-clear-btn"
            :aria-label="$t('common.clearSearchAria')"
            @click="searchQuery = ''"
          >
            ×
          </button>
        </div>
      </header>

      <div class="place-hero">
        <button type="button" class="hero-back" @click="goBack">‹</button>
        <img v-if="placeImageUrl" :src="placeImageUrl" class="hero-photo" alt="" />
        <span v-else class="hero-placeholder">{{ $t('board.photoPlaceholder', { name: placeName }) }}</span>
      </div>

      <div class="place-info-bar">
        <div class="place-name-row">
          <span class="place-name">{{ placeName }}</span>
          <span class="place-cat" :style="{ color: placeCategoryColor }">{{ placeCategory ? $t(`common.category.${placeCategory}`) : '' }}</span>
        </div>
        <div class="place-address">{{ placeAddress }}</div>
      </div>

      <div class="place-tabs">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'posts' }"
          @click="activeTab = 'posts'"
        >{{ $t('board.postsTab', { count: filteredPosts.length }) }}</button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'chat' }"
          @click="activeTab = 'chat'"
        >{{ $t('board.chatTab') }}</button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === 'route' }"
          @click="activeTab = 'route'"
        >{{ $t('board.routeTab') }}</button>
      </div>

      <template v-if="activeTab === 'posts'">
        <div class="list-toolbar">
          <router-link :to="`/locations/${$route.params.location_id}/posts/new`" class="write-btn"><span class="write-icon">+</span>{{ $t('board.writeButton') }}</router-link>
          <button type="button" class="route-toolbar-btn" @click="goToRouteTab">{{ $t('board.findRouteButton') }}</button>
        </div>

        <div class="panel-body">
          <div v-if="loading" class="status-message">{{ $t('board.loadingPosts') }}</div>
          <div v-else-if="error" class="status-message error">{{ error }}</div>
          <div v-else class="post-list">
            <router-link v-for="post in filteredPosts" :key="post.id" :to="`/locations/${$route.params.location_id}/posts/${post.id}`" class="post-item">
              <span class="post-title">{{ post.title }}</span>
              <p class="post-preview">{{ postTranslationState[post.id]?.isTranslated ? postTranslationState[post.id].translatedText : post.content }}</p>
              <div class="post-meta">
                <span>{{ post.author }}</span>
                <span>{{ formatDate(post.created_at) }}</span>
                <span>{{ $t('board.commentCountShort', { count: post.comments?.length || 0 }) }}</span>
                <button type="button" class="translate-btn" @click.prevent="togglePostTranslation(post)" :disabled="postTranslationState[post.id]?.loading">
                  <template v-if="postTranslationState[post.id]?.loading">...</template>
                  <template v-else-if="postTranslationState[post.id]?.isTranslated">{{ locale === 'en' ? 'View Original' : '원문 보기' }}</template>
                  <template v-else>{{ locale === 'en' ? 'View Translation' : '번역 보기' }}</template>
                </button>
              </div>
            </router-link>
            <div v-if="filteredPosts.length === 0" class="empty-row">
              <div class="empty-title">{{ $t('board.noPostsTitle') }}</div>
              <div class="empty-sub">{{ $t('board.noPostsDesc') }}</div>
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="activeTab === 'route'" class="panel-body route-panel">
        <div class="route-panel-inner">
          <DestinationSearch :model-value="mapStore.routeDestination" @update:model-value="mapStore.setRouteDestination" />

          <div class="route-mode-tabs">
            <button
              type="button"
              class="route-mode-btn"
              :class="{ active: mapStore.routeMode === 'car' }"
              @click="mapStore.setRouteMode('car')"
            >{{ $t('board.routeModeCar') }}</button>
            <button
              type="button"
              class="route-mode-btn"
              :class="{ active: mapStore.routeMode === 'transit' }"
              @click="mapStore.setRouteMode('transit')"
            >{{ $t('board.routeModeTransit') }}</button>
          </div>

          <div v-if="!mapStore.routeDestination" class="route-state">
            <div class="route-state-icon">🧭</div>
            <div class="route-state-title">{{ $t('board.routeSelectDestination') }}</div>
          </div>

          <div v-else-if="mapStore.routeLoading" class="route-state">
            <div class="route-state-icon">📍</div>
            <div class="route-state-title">{{ $t('board.routeLocating') }}</div>
          </div>

          <div v-else-if="mapStore.routeError" class="route-state">
            <div class="route-state-icon">⚠️</div>
            <p class="route-error">{{ mapStore.routeError }}</p>
            <button type="button" class="route-retry-btn" @click="mapStore.fetchRoutes()">{{ $t('board.routeRetry') }}</button>
          </div>

          <template v-else-if="routeCandidates.length > 0">
            <RouteMiniMap :path="mapStore.routePath" :segments="mapStore.routeSegments" class="route-result-map" />

            <div class="route-candidate-list">
              <button
                v-for="(candidate, index) in routeCandidates"
                :key="index"
                type="button"
                class="route-candidate-card"
                :class="{ selected: mapStore.selectedCandidateIndex === index }"
                @click="mapStore.selectCandidate(index)"
              >
                <div class="route-candidate-top">
                  <span class="route-candidate-duration">{{ formatDuration(candidate.duration) }}</span>
                  <span class="route-candidate-distance">{{ formatDistance(candidate.distance) }}</span>
                </div>
                <div class="route-candidate-arrival">{{ $t('board.routeArrival', { time: formatArrival(candidate.duration) }) }}</div>

                <div v-if="mapStore.routeMode === 'car'" class="route-candidate-badge">{{ candidate.label }}</div>

                <div v-else class="route-candidate-transit">
                  <div class="route-chip-row">
                    <span
                      v-for="(segment, sIdx) in candidate.segments"
                      :key="sIdx"
                      class="route-chip"
                      :class="`route-chip-${segment.mode}`"
                    >
                      <template v-if="segment.mode === 'walk'">{{ $t('board.routeWalkMinutes', { minutes: Math.max(1, Math.round(segment.duration / 60)) }) }}</template>
                      <template v-else-if="segment.mode === 'subway'">🚇 {{ segment.label }}</template>
                      <template v-else>🚌 {{ segment.label }}</template>
                    </span>
                  </div>
                  <div class="route-transfer-count">{{ $t('board.routeTransferCount', { count: candidate.transfer_count }) }}</div>
                </div>
              </button>
            </div>

            <button type="button" class="route-close-btn" @click="mapStore.clearRoute()">{{ $t('board.routeClear') }}</button>
          </template>

          <div v-else class="route-state">
            <div class="route-state-icon">🚗</div>
            <div class="route-state-title">{{ $t('board.routeCandidateEmpty') }}</div>
          </div>
        </div>
      </div>

      <PlaceChatPanel v-else :location-id="route.params.location_id" />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMapStore } from '@/stores/mapStore'
import PlaceChatPanel from '@/components/chat/PlaceChatPanel.vue'
import RouteMiniMap from '@/components/map/RouteMiniMap.vue'
import DestinationSearch from '@/components/map/DestinationSearch.vue'
import LangSwitcher from '@/components/common/LangSwitcher.vue'
import api from '../api'

const router = useRouter()
const route = useRoute()
const mapStore = useMapStore()
const { t, locale } = useI18n()

const posts = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const activeTab = ref('posts')

const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')

const toggleTheme = () => {
  isDark.value = !isDark.value
  const newTheme = isDark.value ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', newTheme)
  localStorage.setItem('theme', newTheme)
}

const postTranslationState = ref({})

const togglePostTranslation = async (post) => {
  const state = postTranslationState.value[post.id] || { isTranslated: false, translatedText: '', loading: false }
  
  if (state.isTranslated) {
    postTranslationState.value[post.id] = { ...state, isTranslated: false }
    return
  }
  if (state.translatedText) {
    postTranslationState.value[post.id] = { ...state, isTranslated: true }
    return
  }
  
  postTranslationState.value[post.id] = { ...state, loading: true }
  try {
    const target_lang = locale.value === 'en' ? 'en' : 'ko'
    const { data } = await api.post('/translate', {
      text: post.content,
      target_lang
    })
    postTranslationState.value[post.id] = {
      loading: false,
      isTranslated: true,
      translatedText: data.translated
    }
  } catch (err) {
    console.error('Translation error', err)
    postTranslationState.value[post.id] = { ...state, loading: false }
  }
}

// 스토어에서 선택된 장소 정보를 우선 표시하고, API로 받아온 상세 정보로 보강 (새로고침/직접 진입 대응)
const location = ref(null)

const placeName = computed(() => {
  const loc = location.value || mapStore.selectedLocation
  if (!loc) return t('board.allPlaces')
  return locale.value === 'en' ? loc.name_en || loc.name : loc.name
})
const placeCategory = computed(() => location.value?.category || mapStore.selectedLocation?.category || '')

// 지도 마커 색상(카테고리별)과 동일한 팔레트 (style.css --cat-* 토큰 기준)
const CATEGORY_COLORS = {
  '관광지': 'var(--cat-tour)',
  '음식점': 'var(--cat-food)',
  '문화시설': 'var(--cat-culture)',
  '쇼핑': 'var(--cat-shopping)',
  '숙박': 'var(--cat-stay)',
  '레포츠': 'var(--cat-leports)',
  '축제공연행사': 'var(--cat-festival)',
  '여행코스': 'var(--cat-course)'
}
const placeCategoryColor = computed(() => CATEGORY_COLORS[placeCategory.value] || 'var(--cat-tour)')
const placeAddress = computed(() => {
  const loc = location.value || mapStore.selectedLocation
  if (!loc) return ''
  return locale.value === 'en' ? loc.address_en || loc.address : loc.address
})

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

// 목록 상단의 빠른 길찾기 버튼: 길찾기 탭으로 전환만 하면, activeTab watcher가 목적지 자동 설정을 처리
const goToRouteTab = () => {
  activeTab.value = 'route'
}

// route 탭에 처음 진입했을 때(목적지가 아직 없을 때) 현재 보고 있는 장소를 기본 목적지로 채워준다.
// place-tabs의 "길찾기" 탭을 직접 눌러 들어온 경우도 함께 처리하기 위해 watch로 감지.
watch(activeTab, (tab) => {
  if (tab !== 'route' || mapStore.routeDestination) return

  const destLat = location.value?.latitude ?? mapStore.selectedLocation?.latitude
  const destLng = location.value?.longitude ?? mapStore.selectedLocation?.longitude
  if (destLat == null || destLng == null) return

  mapStore.setRouteDestination({ lat: destLat, lng: destLng, name: placeName.value })
})

const routeCandidates = computed(() => {
  return mapStore.routeMode === 'car' ? mapStore.carCandidates : mapStore.transitCandidates
})

const formatDuration = (seconds) => {
  if (seconds == null) return ''
  const minutes = Math.max(1, Math.round(seconds / 60))
  return t('board.routeDurationMinutes', { minutes })
}

const formatDistance = (meters) => {
  if (meters == null) return ''
  return meters >= 1000 ? `${(meters / 1000).toFixed(1)}km` : `${meters}m`
}

const formatArrival = (durationSeconds) => {
  const arrival = new Date(Date.now() + (durationSeconds || 0) * 1000)
  const hh = String(arrival.getHours()).padStart(2, '0')
  const mm = String(arrival.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
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
  return new Date(value).toLocaleDateString(locale.value === 'en' ? 'en-US' : 'ko-KR')
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
    error.value = t('board.fetchPostsError')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  isDark.value = document.documentElement.getAttribute('data-theme') === 'dark'
  fetchLocation()
  fetchPosts()
})

// 다른 장소로 이동/이탈 시 지도에 이전 경로·플로팅 정보가 남지 않도록 정리
onUnmounted(() => {
  mapStore.clearRoute()
  mapStore.clearSelectedLocation()
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
    mapStore.clearRoute()
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
  border-bottom: 1px solid var(--border-hairline);
  flex: none;
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
  background: var(--surface-muted);
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

.search-clear-btn {
  flex: none;
  width: 18px;
  height: 18px;
  border: none;
  border-radius: 50%;
  background: #d8d5cd;
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
  background: #b0ada5;
}

.place-hero {
  position: relative;
  height: 200px;
  flex: none;
  background: repeating-linear-gradient(45deg, var(--surface-muted), var(--surface-muted) 11px, var(--surface-sunken) 11px, var(--surface-sunken) 22px);
}

.hero-back {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--surface);
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
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.place-info-bar {
  padding: 15px 16px 13px;
  flex: none;
  border-bottom: 1px solid var(--border-color);
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
  background: var(--surface-muted);
  padding: 3px 9px;
  border-radius: 20px;
}

.place-address {
  margin-top: 9px;
  color: var(--text-secondary);
  font-size: 13.5px;
  line-height: 1.5;
}

.route-toolbar-btn {
  background: var(--surface-muted);
  color: var(--text-primary);
  border: none;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  margin-left: 8px;
}

.route-panel {
  display: block;
  padding: 20px 18px 32px;
}

.route-panel-inner {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 560px;
  margin: 0 auto;
}

.route-mode-tabs {
  display: flex;
  gap: 8px;
  background: var(--surface-muted);
  border-radius: 12px;
  padding: 4px;
}

.route-mode-btn {
  flex: 1;
  border: none;
  background: transparent;
  border-radius: 9px;
  padding: 9px 10px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.route-mode-btn.active {
  background: var(--surface);
  color: var(--accent);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.route-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 36px 12px;
}

.route-result-map {
  margin-bottom: 4px;
}

.route-state-icon {
  font-size: 34px;
  margin-bottom: 12px;
}

.route-state-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-primary);
}

.route-state-desc {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.55;
}

.route-retry-btn {
  margin-top: 18px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 11px;
  padding: 12px 22px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(241, 91, 76, 0.2);
}

.route-candidate-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.route-candidate-card {
  display: block;
  width: 100%;
  text-align: left;
  background: var(--surface);
  border: 1.5px solid var(--border-hairline);
  border-radius: 14px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.route-candidate-card:hover {
  border-color: var(--border-input);
}

.route-candidate-card.selected {
  border-color: var(--accent);
  box-shadow: 0 6px 18px rgba(241, 91, 76, 0.16);
}

.route-candidate-top {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.route-candidate-duration {
  font-size: 19px;
  font-weight: 800;
  color: var(--text-primary);
}

.route-candidate-distance {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent);
}

.route-candidate-arrival {
  margin-top: 3px;
  font-size: 12px;
  color: var(--text-muted);
}

.route-candidate-badge {
  margin-top: 10px;
  display: inline-block;
  background: var(--surface-muted);
  color: var(--text-primary);
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 20px;
}

.route-candidate-transit {
  margin-top: 10px;
}

.route-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.route-chip {
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 9px;
  border-radius: 20px;
  color: #fff;
}

.route-chip-walk {
  background: #9ca3af;
}

.route-chip-bus {
  background: #22c55e;
}

.route-chip-subway {
  background: #3b82f6;
}

.route-transfer-count {
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--text-muted);
}

.route-close-btn {
  align-self: center;
  margin-top: 4px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 12.5px;
  cursor: pointer;
  padding: 0;
}

.route-error {
  margin: 10px 0 0;
  color: var(--danger-text);
  font-size: 12.5px;
}

.place-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-hairline);
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
  border-bottom: 1px solid var(--border-hairline);
  padding: 15px 16px;
  cursor: pointer;
  color: inherit;
  transition: background-color 0.2s ease;
}

.post-item:hover {
  background: var(--surface-hover);
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
  color: var(--text-secondary);
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

.translate-btn {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 11.5px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  margin-left: 8px;
}

.translate-btn:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
  text-decoration: none;
}

.status-message {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.status-message.error {
  color: var(--danger-text);
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

/* 모바일 하단 시트에서는 히어로가 세로 공간을 과하게 먹지 않도록 축소 */
@media (max-width: 768px) {
  .place-hero {
    height: 140px;
  }
}
</style>
