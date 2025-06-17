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
    const csrfToken = localStorage.getItem('csrf_token')
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }
    
    // 모바일만 Authorization 헤더 사용
    if (isMobile()) {
      const accessToken = localStorage.getItem('access_token')
      if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`
        console.log('[REQUEST] Mobile: Using Authorization header')
      }
      
      // refresh 요청일 때 X-Refresh-Token 헤더 추가 (모바일만)
      if (config.url === '/auth/refresh') {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          config.headers['X-Refresh-Token'] = refreshToken
        }
      }
    } else {
      console.log('[REQUEST] Desktop: Using cookies only')
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
        // 모바일만 localStorage 삭제
        if (isMobile()) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
        localStorage.removeItem('csrf_token')
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
          localStorage.setItem('csrf_token', refreshResponse.data.csrf_token)
        }
        
        processQueue(null, refreshResponse.data.csrf_token)
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        
        // 모바일만 localStorage 삭제
        if (isMobile()) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
        localStorage.removeItem('csrf_token')
        
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