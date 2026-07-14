import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useMapStore = defineStore('map', () => {
  const locations = ref([])
  const isLoading = ref(false)
  const selectedLocation = ref(null)

  const fetchLocations = async (category = null, q = null) => {
    isLoading.value = true
    try {
      const params = {}
      if (category) params.category = category
      if (q) params.q = q
      
      const response = await api.get('/locations/', { params })
      locations.value = response.data
    } catch (error) {
      console.error('장소 목록 불러오기 실패:', error)
    } finally {
      isLoading.value = false
    }
  }

  const selectLocation = (loc) => {
    selectedLocation.value = loc
    // 여기서 MapView 컴포넌트 내의 지도 중심 이동 등을 트리거할 수 있습니다.
  }

  return {
    locations,
    isLoading,
    selectedLocation,
    fetchLocations,
    selectLocation
  }
})
