import api from './index'

// history: [{ role: 'user' | 'assistant', content: string }]
// 반환값: { reply: string, locations: LocationBrief[] } — locations는 LLM이 답변에서 실제 언급한 장소
export const postChat = async (message, history) => {
  const { data } = await api.post('/chat', { message, history })
  return { reply: data.reply, locations: data.locations || [] }
}

// 장소별 실시간 채팅(§5.4) 최근 이력 조회
export const getChatHistory = async (locationId) => {
  const { data } = await api.get(`/chat/rooms/${locationId}/messages`)
  return data
}

// 장소별 실시간 채팅 WebSocket 접속 URL
export const getPlaceChatSocketUrl = (locationId) => {
  const base = import.meta.env.VITE_API_BASE_URL.replace(/^http/, 'ws')
  return `${base}/api/chat/ws/${locationId}`
}
