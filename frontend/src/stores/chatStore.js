import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getChatHistory, getPlaceChatSocketUrl } from '../api/chat'

let messageSeq = 0
const nextId = () => `m-${Date.now()}-${messageSeq++}`

export const usePlaceChatStore = defineStore('placeChat', () => {
  const messages = ref([])
  const nickname = ref('')
  const status = ref('idle') // idle | connecting | open | closed | error

  let socket = null

  const reset = () => {
    messages.value = []
    nickname.value = ''
    status.value = 'idle'
  }

  const connect = async (locationId) => {
    disconnect()
    reset()
    status.value = 'connecting'

    try {
      const history = await getChatHistory(locationId)
      messages.value = history.map((m) => ({
        id: nextId(),
        type: 'message',
        nickname: m.nickname,
        content: m.content,
      }))
    } catch (err) {
      // 이력 조회 실패해도 실시간 접속은 시도
    }

    socket = new WebSocket(getPlaceChatSocketUrl(locationId))

    socket.onopen = () => {
      status.value = 'open'
    }

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      if (payload.type === 'self') {
        nickname.value = payload.nickname
        return
      }
      messages.value.push({
        id: nextId(),
        type: payload.type,
        nickname: payload.nickname,
        content: payload.content,
      })
    }

    socket.onclose = () => {
      status.value = 'closed'
    }

    socket.onerror = () => {
      status.value = 'error'
    }
  }

  const sendMessage = (content) => {
    const trimmed = content.trim()
    if (!trimmed || !socket || socket.readyState !== WebSocket.OPEN) return
    socket.send(JSON.stringify({ content: trimmed }))
  }

  const disconnect = () => {
    if (socket) {
      socket.onopen = null
      socket.onmessage = null
      socket.onclose = null
      socket.onerror = null
      socket.close()
      socket = null
    }
  }

  return {
    messages,
    nickname,
    status,
    connect,
    sendMessage,
    disconnect,
  }
})
