import axios from 'axios'


const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 5000,
  withCredentials: true, // Access/Refresh 쿠키 자동 포함
  headers: {
    'Content-Type': 'application/json',
  },
})


function getCSRFToken() {
  const match = document.cookie.match(/(^|;)\s*csrf_token=([^;]+)/)
  return match ? match[2] : null
}

// ✅ 요청 인터셉터: CSRF 토큰 추가
axiosInstance.interceptors.request.use(
  (config) => {
    const csrfToken = getCSRFToken()
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }
    return config
  },
  (error) => Promise.reject(error)
)


axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true
      try {
        await axiosInstance.post('/auth/refresh') // refresh 토큰으로 access 갱신
        return axiosInstance(error.config) // 요청 재시도
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        // redirect to login if needed
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance