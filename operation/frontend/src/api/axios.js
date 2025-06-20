import axios from 'axios'

// 모바일 감지
const isMobile = () => {
  return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

axiosInstance.interceptors.request.use(
  (config) => {
    // CSRF 토큰을 매번 새로 가져오기 (안전한 접근)
    let csrfToken = null
    try {
      csrfToken = sessionStorage.getItem('csrf_token')
    } catch (e) {
      // sessionStorage 접근 실패 시 무시
    }
    
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }
    
    // sessionStorage에 access_token이 있으면 항상 Authorization 헤더에 설정 (소셜 로그인 지원)
    const accessToken = sessionStorage.getItem('access_token')
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`
      console.log('[AXIOS] Using sessionStorage access_token for Authorization header')
    } else if (!isMobile()) {
      // sessionStorage에 토큰이 없고 데스크톱이면 쿠키 사용 (일반 로그인)
      console.log('[AXIOS] Using cookies for desktop authentication')
    }
    
    // refresh 요청일 때 X-Refresh-Token 헤더 추가
    if (config.url === '/auth/refresh') {
      const refreshToken = sessionStorage.getItem('refresh_token')
      if (refreshToken) {
        config.headers['X-Refresh-Token'] = refreshToken
        console.log('[AXIOS] Adding X-Refresh-Token header for refresh request')
      }
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url === '/auth/refresh') {
        // refresh 실패 시 모든 sessionStorage 토큰 삭제
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('refresh_token')
        sessionStorage.removeItem('csrf_token')
        console.log('[AXIOS] Refresh failed - all tokens cleared')
        window.location.href = '/login'
        return Promise.reject(error)
      }
      
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => {
          return axiosInstance(originalRequest)
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        const refreshResponse = await axiosInstance.post('/auth/refresh')
        
        // CSRF 토큰 업데이트
        if (refreshResponse.data.csrf_token) {
          sessionStorage.setItem('csrf_token', refreshResponse.data.csrf_token)
        }
        
        // 새로운 access_token이 있으면 업데이트 (소셜 로그인 지원)
        if (refreshResponse.data.access_token) {
          sessionStorage.setItem('access_token', refreshResponse.data.access_token)
          console.log('[AXIOS] New access_token saved to sessionStorage after refresh')
        }
        
        processQueue(null, refreshResponse.data.csrf_token)
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        
        // 모든 sessionStorage 토큰 삭제
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('refresh_token')
        sessionStorage.removeItem('csrf_token')
        console.log('[AXIOS] Authentication failed - all tokens cleared')
        
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance