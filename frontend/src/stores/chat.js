import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { postChat } from '../api/chat'
import { useMapStore } from './mapStore'

const INITIAL_MESSAGE = {
  id: 1,
  sender: 'system',
  text: '안녕하세요! 서울 관광지나 여행에 대해 물어보세요.'
}

// API로 전송할 히스토리에 포함할 최근 메시지 수 (user+assistant 합산 상한)
const MAX_HISTORY_MESSAGES = 12

// 취향을 자유 입력 대신 정해진 태그 중에서 고르도록 제한 (모드별 선택지)
const TAG_OPTIONS = {
  taste: ['맛집', '자연', '문화/전시', '쇼핑', '숙박', '관광지'],
  mood: ['조용한', '활기찬', '로맨틱', '힐링', '사진 찍기 좋은', '가족 친화적']
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref([{ ...INITIAL_MESSAGE }])
  const isLoading = ref(false)
  const isOpen = ref(false)

  // 취향 선택 카드 상태 — 자유 텍스트 대신 모드(취향/기분)를 고르고 정해진 태그만 다중 선택.
  // 서버/localStorage에 영속 저장하지 않고 세션 동안만 유지.
  const showPreferencePrompt = ref(true)
  const preferenceMode = ref(null) // 'taste' | 'mood' | null
  const selectedTags = ref([])

  const currentTagOptions = computed(() => TAG_OPTIONS[preferenceMode.value] || [])
  const preferences = computed(() => selectedTags.value.join(', '))

  const selectPreferenceMode = (mode) => {
    preferenceMode.value = mode
    selectedTags.value = []
  }

  const toggleTag = (tag) => {
    const idx = selectedTags.value.indexOf(tag)
    if (idx === -1) selectedTags.value.push(tag)
    else selectedTags.value.splice(idx, 1)
  }

  const confirmPreferences = () => {
    showPreferencePrompt.value = false
  }

  const skipPreferences = () => {
    preferenceMode.value = null
    selectedTags.value = []
    showPreferencePrompt.value = false
  }

  const reopenPreferencePrompt = () => {
    showPreferencePrompt.value = true
  }

  const addMessage = (sender, text, locations = []) => {
    messages.value.push({
      id: Date.now(),
      sender,
      text,
      locations
    })
  }

  // 챗봇이 추천한 장소 중 첫 번째로 지도를 이동시키고, 검색창도 같은 키워드로 채워 목록을 필터링
  const focusOnLocation = (loc) => {
    const mapStore = useMapStore()
    mapStore.selectLocation(loc)
    mapStore.setSearchQuery(loc.name)
    mapStore.fetchLocations(null, loc.name)
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const clearMessages = () => {
    messages.value = [{ ...INITIAL_MESSAGE }]
  }

  const toggleOpen = () => {
    isOpen.value = !isOpen.value
  }

  const sendMessage = async (text) => {
    const trimmed = text.trim()
    if (!trimmed || isLoading.value) return

    // 실제 대화(user/ai)만 히스토리로 전송 — 초기 인사말/오류 안내는 제외
    const history = messages.value
      .filter((m) => m.sender === 'user' || m.sender === 'ai')
      .slice(-MAX_HISTORY_MESSAGES)
      .map((m) => ({ role: m.sender === 'user' ? 'user' : 'assistant', content: m.text }))

    addMessage('user', trimmed)
    setLoading(true)
    try {
      const { reply, locations } = await postChat(trimmed, history, preferences.value.trim())
      addMessage('ai', reply, locations)
      if (locations.length > 0) {
        focusOnLocation(locations[0])
      }
    } catch (err) {
      addMessage('system', '죄송합니다, 답변을 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.')
    } finally {
      setLoading(false)
    }
  }

  return {
    messages,
    isLoading,
    isOpen,
    showPreferencePrompt,
    preferenceMode,
    selectedTags,
    currentTagOptions,
    preferences,
    selectPreferenceMode,
    toggleTag,
    confirmPreferences,
    skipPreferences,
    reopenPreferencePrompt,
    addMessage,
    setLoading,
    clearMessages,
    toggleOpen,
    sendMessage,
    focusOnLocation
  }
})
