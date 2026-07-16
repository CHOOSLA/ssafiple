<template>
  <div class="destination-search">
    <div class="destination-search-input-row">
      <svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true">
        <circle cx="7" cy="7" r="5" fill="none" stroke="#9a968f" stroke-width="2" />
        <line x1="10.8" y1="10.8" x2="15" y2="15" stroke="#9a968f" stroke-width="2" stroke-linecap="round" />
      </svg>
      <input
        v-model="query"
        type="text"
        :placeholder="$t('board.destinationSearchPlaceholder')"
        @focus="onFocus"
      />
      <button
        v-if="query"
        type="button"
        class="destination-clear-btn"
        :aria-label="$t('common.clearSearchAria')"
        @click="handleClear"
      >
        ×
      </button>
    </div>

    <ul v-if="showResults && results.length > 0" class="destination-results">
      <li v-for="item in results" :key="item.id" class="destination-result-item">
        <button type="button" @click="selectResult(item)">
          <span class="destination-result-name">{{ item.place_name }}</span>
          <span class="destination-result-address">{{ item.address_name }}</span>
        </button>
      </li>
    </ul>
    <div v-else-if="showResults && searched && results.length === 0" class="destination-empty">
      {{ $t('board.destinationSearchEmpty') }}
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { waitForKakao } from '@/utils/kakaoLoader'

const props = defineProps({
  modelValue: { type: Object, default: null } // { lat, lng, name } | null
})

const emit = defineEmits(['update:modelValue'])

const query = ref(props.modelValue?.name || '')
const results = ref([])
const showResults = ref(false)
const searched = ref(false)
let debounceTimer = null
let placesService = null

const getPlacesService = async () => {
  if (placesService) return placesService
  await waitForKakao()
  placesService = new window.kakao.maps.services.Places()
  return placesService
}

const runSearch = async (keyword) => {
  const trimmed = keyword.trim()
  if (!trimmed) {
    results.value = []
    searched.value = false
    showResults.value = false
    return
  }

  try {
    const places = await getPlacesService()
    places.keywordSearch(trimmed, (data, status) => {
      searched.value = true
      if (status === window.kakao.maps.services.Status.OK) {
        results.value = data.slice(0, 5)
      } else {
        results.value = []
      }
      showResults.value = true
    })
  } catch (err) {
    console.error('장소 검색 실패:', err)
    results.value = []
  }
}

watch(query, (value) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => runSearch(value), 300)
})

const onFocus = () => {
  if (results.value.length > 0) showResults.value = true
}

const selectResult = (item) => {
  query.value = item.place_name
  showResults.value = false
  emit('update:modelValue', {
    lat: Number(item.y),
    lng: Number(item.x),
    name: item.place_name
  })
}

const handleClear = () => {
  query.value = ''
  results.value = []
  showResults.value = false
  searched.value = false
}

watch(
  () => props.modelValue,
  (value) => {
    if (value?.name && value.name !== query.value) {
      query.value = value.name
    }
  }
)

onBeforeUnmount(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped>
.destination-search {
  position: relative;
}

.destination-search-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f4f2ee;
  border-radius: 11px;
  padding: 10px 12px;
}

.destination-search-input-row input {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  min-width: 0;
  font-size: 14px;
  color: var(--text-primary);
}

.destination-clear-btn {
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

.destination-clear-btn:hover {
  background: #b0ada5;
}

.destination-results {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 20;
  background: #fff;
  border: 1px solid #eceae6;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  max-height: 260px;
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 4px;
}

.destination-result-item button {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-radius: 9px;
  padding: 9px 10px;
  cursor: pointer;
  gap: 2px;
}

.destination-result-item button:hover {
  background: #f6f5f2;
}

.destination-result-name {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.destination-result-address {
  font-size: 12px;
  color: var(--text-muted);
}

.destination-empty {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 20;
  background: #fff;
  border: 1px solid #eceae6;
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
  padding: 14px;
  text-align: center;
  font-size: 12.5px;
  color: var(--text-muted);
}
</style>
