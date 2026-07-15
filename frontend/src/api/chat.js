import api from './index'

// history: [{ role: 'user' | 'assistant', content: string }]
// preferences: 매 요청마다 그때그때 입력하는 취향 힌트 (서버에 영속 저장되지 않음)
// 반환값: { reply: string, locations: LocationBrief[] } — locations는 LLM이 답변에서 실제 언급한 장소
export const postChat = async (message, history, preferences = '') => {
  const { data } = await api.post('/chat', { message, history, preferences })
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
