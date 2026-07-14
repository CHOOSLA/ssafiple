import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([
    {
      id: 1,
      sender: 'system',
      text: '안녕하세요! 서울 관광지나 여행에 대해 물어보세요.'
    }
  ])
  const isLoading = ref(false)

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
    messages.value = [
      {
        id: 1,
        sender: 'system',
        text: '안녕하세요! 서울 관광지나 여행에 대해 물어보세요.'
      }
    ]
  }

  return {
    messages,
    isLoading,
    addMessage,
    setLoading,
    clearMessages
  }
})
