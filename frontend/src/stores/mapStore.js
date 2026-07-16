import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axios from 'axios'
import api from '@/api'

const ODSAY_TRANSIT_URL = 'https://api.odsay.com/v1/api/searchPubTransPathT'

const getOdsayErrorMessage = (error) => {
  if (!error) return ''
  if (Array.isArray(error)) {
    return error[0]?.message || error[0]?.msg || String(error[0] || '')
  }
  return error.message || error.msg || String(error)
}

const isValidRoutePoint = (point) => {
  return Number.isFinite(point.lat)
    && Number.isFinite(point.lng)
    && point.lat >= 33
    && point.lat <= 39
    && point.lng >= 124
    && point.lng <= 132
}

const createRoutePoint = (lng, lat) => {
  const point = {
    lat: Number(lat),
    lng: Number(lng),
  }
  return isValidRoutePoint(point) ? point : null
}

const uniqueRoutePoints = (points) => {
  const result = []
  points.filter(Boolean).forEach((point) => {
    const prev = result[result.length - 1]
    if (!prev || prev.lat !== point.lat || prev.lng !== point.lng) {
      result.push(point)
    }
  })
  return result
}

const getTransitSegmentPath = (sub) => {
  const points = [
    createRoutePoint(sub.startX, sub.startY),
    ...((sub.passStopList?.stations || []).map((station) => createRoutePoint(station.x, station.y))),
    createRoutePoint(sub.endX, sub.endY),
  ]
  return uniqueRoutePoints(points)
}

const normalizeTransitDirections = (data) => {
  const error = data?.error
  if (error) {
    throw new Error(getOdsayErrorMessage(error) || '대중교통 경로를 찾을 수 없습니다.')
  }

  const paths = (data?.result?.path || [])
    .slice()
    .sort((a, b) => (a.info?.totalTime || 0) - (b.info?.totalTime || 0))
    .slice(0, 3)

  if (!paths.length) {
    throw new Error('대중교통 경로를 찾을 수 없습니다.')
  }

  return {
    candidates: paths.map((path) => {
      const info = path.info || {}
      const segments = (path.subPath || []).map((sub) => {
        let mode = 'walk'
        let label = null

        if (sub.trafficType === 1) {
          mode = 'subway'
          label = (sub.lane || [{}])[0]?.name || null
        } else if (sub.trafficType === 2) {
          mode = 'bus'
          label = (sub.lane || [{}])[0]?.busNo || null
        }

        const segmentPath = getTransitSegmentPath(sub)

        return {
          mode,
          label,
          start_name: sub.startName || '',
          end_name: sub.endName || '',
          duration: (sub.sectionTime || 0) * 60,
          distance: sub.distance || 0,
          path: segmentPath,
        }
      }).filter((segment) => segment.path.length >= 2)

      return {
        duration: (info.totalTime || 0) * 60,
        distance: info.totalDistance || 0,
        transfer_count: (info.busTransitCount || 0) + (info.subwayTransitCount || 0),
        walk_distance: info.totalWalk || 0,
        segments,
      }
    }),
  }
}

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

  const clearSelectedLocation = () => {
    selectedLocation.value = null
  }

  // 길찾기(경로 안내) 상태 — 현재 위치 → 사용자가 지정한 목적지
  // 자동차/대중교통 두 모드 각각 상위 경로 후보 리스트를 들고 있다가, 선택된 후보 하나를
  // routePath/routeSegments computed로 뽑아 지도(KakaoMap.vue)와 미니맵(RouteMiniMap.vue)에 넘긴다.
  const routeMode = ref('car') // 'car' | 'transit'
  const routeOrigin = ref(null) // { lat, lng, name } | null
  const routeDestination = ref(null) // { lat, lng, name } | null
  const carCandidates = ref([])
  const transitCandidates = ref([])
  const selectedCandidateIndex = ref(0)
  const routeLoading = ref(false)
  const routeError = ref('')

  // 부트캠프 시연용 고정 출발지 (서울 강남구 테헤란로 212 인근).
  // 실사용자 대상 서비스가 아니라 발표 데모 환경이라, 발표 중 위치 권한 팝업/부정확한
  // 네트워크 기반 위치 추정에 흔들리지 않도록 브라우저 Geolocation 대신 고정 좌표를 사용한다.
  const DEMO_ORIGIN = { latitude: 37.5012746, longitude: 127.0395857 }

  const getCurrentPosition = () => {
    return Promise.resolve({ coords: DEMO_ORIGIN })
  }

  // KakaoMap.vue가 이 이름을 그대로 watch하므로 이름을 유지한다.
  const routePath = computed(() => {
    const candidates = routeMode.value === 'car' ? carCandidates.value : transitCandidates.value
    const candidate = candidates[selectedCandidateIndex.value]
    if (!candidate) return []

    if (routeMode.value === 'car') {
      return candidate.path || []
    }
    return (candidate.segments || []).flatMap((segment) => segment.path || [])
  })

  // 대중교통 모드에서 구간별(도보/버스/지하철) 색상을 구분해 그리기 위한 데이터
  const routeSegments = computed(() => {
    if (routeMode.value !== 'transit') return null
    const candidate = transitCandidates.value[selectedCandidateIndex.value]
    if (!candidate) return null
    return candidate.segments.map((segment) => ({ mode: segment.mode, path: segment.path }))
  })

  const fetchRoutes = async () => {
    if (!routeDestination.value) return

    routeLoading.value = true
    routeError.value = ''

    try {
      const position = await getCurrentPosition()
      routeOrigin.value = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        name: '출발지'
      }

      if (routeMode.value === 'car') {
        const { data } = await api.get('/directions/car', {
          params: {
            origin_lat: position.coords.latitude,
            origin_lng: position.coords.longitude,
            dest_lat: routeDestination.value.lat,
            dest_lng: routeDestination.value.lng
          }
        })
        carCandidates.value = data.candidates
      } else {
        const apiKey = import.meta.env.VITE_ODSAY_API_KEY
        if (!apiKey) {
          throw new Error('VITE_ODSAY_API_KEY가 설정되지 않았습니다.')
        }

        const { data } = await axios.get(ODSAY_TRANSIT_URL, {
          params: {
            SX: position.coords.longitude,
            SY: position.coords.latitude,
            EX: routeDestination.value.lng,
            EY: routeDestination.value.lat,
            OPT: 0,
            apiKey
          },
          timeout: 30000
        })

        const normalized = normalizeTransitDirections(data)
        transitCandidates.value = normalized.candidates
      }
      selectedCandidateIndex.value = 0
    } catch (err) {
      console.error('경로 조회 실패:', err)
      routeError.value = err?.message || '경로를 찾을 수 없습니다.'
    } finally {
      routeLoading.value = false
    }
  }

  const setRouteDestination = (dest) => {
    routeDestination.value = dest
    fetchRoutes()
  }

  const setRouteMode = (mode) => {
    routeMode.value = mode
    selectedCandidateIndex.value = 0
    if (routeDestination.value) {
      fetchRoutes()
    }
  }

  const selectCandidate = (index) => {
    selectedCandidateIndex.value = index
  }

  const clearRoute = () => {
    routeOrigin.value = null
    routeDestination.value = null
    carCandidates.value = []
    transitCandidates.value = []
    routeError.value = ''
    selectedCandidateIndex.value = 0
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
    clearSelectedLocation,
    setSearchQuery,
    setCategoryFilter,
    routeMode,
    routeOrigin,
    routeDestination,
    carCandidates,
    transitCandidates,
    selectedCandidateIndex,
    routeLoading,
    routeError,
    routePath,
    routeSegments,
    fetchRoutes,
    setRouteDestination,
    setRouteMode,
    selectCandidate,
    clearRoute
  }
})
