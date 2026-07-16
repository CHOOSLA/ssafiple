import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useMapStore = defineStore('map', () => {
  const locations = ref([])
  const isLoading = ref(false)
  const isFetchingMore = ref(false)
  const selectedLocation = ref(null)
  
  // 무한 스크롤 상태
  const skip = ref(0)
  const limit = ref(200)
  const hasMore = ref(true)
  
  // 줌 레벨 너무 축소 시 안내용 상태
  const isZoomOutTooMuch = ref(false)
  
  // 현재 검색/필터 상태 캐시
  const currentQuery = ref({ category: null, q: null, bbox: null })

  // 검색창(PlaceListPanel) 입력값 — 챗봇 등 외부에서 검색어를 주입할 수 있도록 store로 관리
  const searchQuery = ref('')

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  // 카테고리 필터 상태 (null = 전체 보기) — CategoryFilter 컴포넌트에서 갱신
  const categoryFilter = ref(null)

  const setCategoryFilter = (category) => {
    categoryFilter.value = category
  }

  const fetchLocations = async (category = null, q = null, bbox = null) => {
    isLoading.value = true
    skip.value = 0
    hasMore.value = true
    currentQuery.value = { category, q, bbox }
    
    try {
      const params = { skip: skip.value, limit: limit.value }
      if (category) params.category = category
      if (q) params.q = q
      if (bbox) {
        Object.assign(params, bbox)
      }
      
      const response = await api.get('/locations/', { params })
      const data = Array.isArray(response?.data) ? response.data : []
      locations.value = data
      
      if (data.length < limit.value) {
        hasMore.value = false
      }
    } catch (error) {
      console.error('장소 목록 불러오기 실패:', error)
      locations.value = []
    } finally {
      isLoading.value = false
    }
  }

  const fetchMoreLocations = async () => {
    if (isFetchingMore.value || !hasMore.value || isLoading.value) return
    
    isFetchingMore.value = true
    skip.value += limit.value
    
    try {
      const params = { skip: skip.value, limit: limit.value }
      if (currentQuery.value.category) params.category = currentQuery.value.category
      if (currentQuery.value.q) params.q = currentQuery.value.q
      if (currentQuery.value.bbox) {
        Object.assign(params, currentQuery.value.bbox)
      }
      
      const response = await api.get('/locations/', { params })
      if (response.data.length > 0) {
        locations.value = [...locations.value, ...response.data]
      }
      
      if (response.data.length < limit.value) {
        hasMore.value = false
      }
    } catch (error) {
      console.error('추가 장소 불러오기 실패:', error)
    } finally {
      isFetchingMore.value = false
    }
  }

  const selectLocation = (loc) => {
    selectedLocation.value = loc
    // 여기서 MapView 컴포넌트 내의 지도 중심 이동 등을 트리거할 수 있습니다.
  }

  // 길찾기(경로 안내) 상태 — 현재 위치 → 선택 장소
  const routePath = ref([])
  const routeInfo = ref(null) // { duration, distance }
  const routeLoading = ref(false)
  const routeError = ref('')

  // 부트캠프 시연용 고정 출발지 (서울 강남구 테헤란로 212 인근).
  // 실사용자 대상 서비스가 아니라 발표 데모 환경이라, 발표 중 위치 권한 팝업/부정확한
  // 네트워크 기반 위치 추정에 흔들리지 않도록 브라우저 Geolocation 대신 고정 좌표를 사용한다.
  const DEMO_ORIGIN = { latitude: 37.5012746, longitude: 127.0395857 }

  const getCurrentPosition = () => {
    return Promise.resolve({ coords: DEMO_ORIGIN })
  }

  const fetchDirections = async (destLat, destLng) => {
    routeLoading.value = true
    routeError.value = ''
    routeInfo.value = null
    routePath.value = []

    try {
      const position = await getCurrentPosition()
      const { data } = await api.get('/directions/', {
        params: {
          origin_lat: position.coords.latitude,
          origin_lng: position.coords.longitude,
          dest_lat: destLat,
          dest_lng: destLng
        }
      })
      routePath.value = data.path
      routeInfo.value = { duration: data.duration, distance: data.distance }
    } catch (err) {
      if (err?.code === 1) {
        // GeolocationPositionError.PERMISSION_DENIED
        routeError.value = '위치 권한이 거부되었습니다. 브라우저 설정에서 위치 접근을 허용해주세요.'
      } else if (err?.code === 2 || err?.code === 3) {
        routeError.value = '현재 위치를 확인할 수 없습니다.'
      } else {
        routeError.value = '경로를 찾을 수 없습니다.'
      }
    } finally {
      routeLoading.value = false
    }
  }

  const clearRoute = () => {
    routePath.value = []
    routeInfo.value = null
    routeError.value = ''
    routeLoading.value = false
  }

  return {
    locations,
    isLoading,
    isFetchingMore,
    hasMore,
    selectedLocation,
    searchQuery,
    categoryFilter,
    isZoomOutTooMuch,
    fetchLocations,
    fetchMoreLocations,
    selectLocation,
    setSearchQuery,
    setCategoryFilter,
    routePath,
    routeInfo,
    routeLoading,
    routeError,
    fetchDirections,
    clearRoute
  }
})
