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
  const limit = ref(50)
  const hasMore = ref(true)
  
  // 현재 검색/필터 상태 캐시
  const currentQuery = ref({ category: null, q: null, bbox: null })

  // 검색창(PlaceListPanel) 입력값 — 챗봇 등 외부에서 검색어를 주입할 수 있도록 store로 관리
  const searchQuery = ref('')

  const setSearchQuery = (query) => {
    searchQuery.value = query
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

  return {
    locations,
    isLoading,
    isFetchingMore,
    hasMore,
    selectedLocation,
    searchQuery,
    fetchLocations,
    fetchMoreLocations,
    selectLocation,
    setSearchQuery
  }
})
