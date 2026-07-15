import api from './index'

// history: [{ role: 'user' | 'assistant', content: string }]
export const postChat = async (message, history) => {
  const { data } = await api.post('/chat', { message, history })
  return data.reply
}
