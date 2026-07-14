import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRouteSelectionStore = defineStore('routeSelection', () => {
  const selectedLocations = ref([])
  const activeLocationId = ref(null)

  const selectLocation = (location) => {
    activeLocationId.value = location.id
    if (!selectedLocations.value.some(loc => loc.id === location.id)) {
      selectedLocations.value.push(location)
    }
  }

  const deselectLocation = (locationId) => {
    selectedLocations.value = selectedLocations.value.filter(loc => loc.id !== locationId)
    if (activeLocationId.value === locationId) {
      activeLocationId.value = selectedLocations.value.length > 0 ? selectedLocations.value[0].id : null
    }
  }

  const setActiveLocation = (locationId) => {
    activeLocationId.value = locationId
  }

  const clearRoute = () => {
    selectedLocations.value = []
    activeLocationId.value = null
  }

  return {
    selectedLocations,
    activeLocationId,
    selectLocation,
    deselectLocation,
    setActiveLocation,
    clearRoute
  }
})
