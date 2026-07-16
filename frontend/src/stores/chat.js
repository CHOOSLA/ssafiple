import { defineStore } from 'pinia'
import { ref } from 'vue'
import { postChat } from '../api/chat'
import { useMapStore } from './mapStore'
import i18n from '../i18n'

const { t, locale } = i18n.global

// 언어 전환 시에도 즉시 갱신되도록, 고정 텍스트 대신 번역 키만 저장하고
// 화면(ChatWidget.vue)에서 렌더링 시점에 $t()로 풀어낸다.
const buildInitialMessage = () => ({
  id: 1,
  sender: 'system',
  textKey: 'chat.welcomeMessage'
})

// API로 전송할 히스토리에 포함할 최근 메시지 수 (user+assistant 합산 상한)
const MAX_HISTORY_MESSAGES = 12

export const useChatStore = defineStore('chat', () => {
  const messages = ref([buildInitialMessage()])
  const isLoading = ref(false)
  const isOpen = ref(false)

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
    messages.value = [buildInitialMessage()]
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
      const { reply, locations } = await postChat(trimmed, history, locale.value === 'en' ? 'en' : 'ko')
      addMessage('ai', reply, locations)
      if (locations.length > 0) {
        focusOnLocation(locations[0])
      }
    } catch (err) {
      addMessage('system', t('chat.replyError'))
    } finally {
      setLoading(false)
    }
  }

  return {
    messages,
    isLoading,
    isOpen,
    addMessage,
    setLoading,
    clearMessages,
    toggleOpen,
    sendMessage,
    focusOnLocation
  }
})
