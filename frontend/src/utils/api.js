import axios from 'axios'

// 환경 변수에서 기본 API 서버 URL을 가져오며, 없을 경우 기본값으로 8000번 포트 사용
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL,
  timeout: 10000,
})

// 향후 토큰 인증이나 공통 에러 처리가 필요할 경우 interceptor를 여기에 추가합니다.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 에러:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api
