import { defineStore } from 'pinia'
import { ref } from 'vue'
import { postChat } from '../api/chat'

const INITIAL_MESSAGE = {
  id: 1,
  sender: 'system',
  text: '안녕하세요! 서울 관광지나 여행에 대해 물어보세요.'
}

// API로 전송할 히스토리에 포함할 최근 메시지 수 (user+assistant 합산 상한)
const MAX_HISTORY_MESSAGES = 12

export const useChatStore = defineStore('chat', () => {
  const messages = ref([{ ...INITIAL_MESSAGE }])
  const isLoading = ref(false)
  const isOpen = ref(false)

  const addMessage = (sender, text) => {
    messages.value.push({
      id: Date.now(),
      sender,
      text
    })
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
      const reply = await postChat(trimmed, history)
      addMessage('ai', reply)
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
    addMessage,
    setLoading,
    clearMessages,
    toggleOpen,
    sendMessage
  }
})
