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
    
    // 모바일만 Authorization 헤더 사용
    if (isMobile()) {
      const accessToken = sessionStorage.getItem('access_token')
      if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`
      }
      
      // refresh 요청일 때 X-Refresh-Token 헤더 추가 (모바일만)
      if (config.url === '/auth/refresh') {
        const refreshToken = sessionStorage.getItem('refresh_token')
        if (refreshToken) {
          config.headers['X-Refresh-Token'] = refreshToken
        }
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
        // 모바일만 sessionStorage 삭제
        if (isMobile()) {
          sessionStorage.removeItem('access_token')
          sessionStorage.removeItem('refresh_token')
        }
        sessionStorage.removeItem('csrf_token')
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
        if (refreshResponse.data.csrf_token) {
          sessionStorage.setItem('csrf_token', refreshResponse.data.csrf_token)
        }
        
        processQueue(null, refreshResponse.data.csrf_token)
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        
        // 모바일만 sessionStorage 삭제
        if (isMobile()) {
          sessionStorage.removeItem('access_token')
          sessionStorage.removeItem('refresh_token')
        }
        sessionStorage.removeItem('csrf_token')
        
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