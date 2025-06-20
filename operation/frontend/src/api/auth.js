import axios from './axios'

// 모바일 감지
const isMobile = () => {
  return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 회원가입
export const signup = async (userData) => {
  try {
    const response = await axios.post('/auth/signup', userData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 로그인
export const login = async (credentials) => {
  try {
    const response = await axios.post('/auth/login', credentials)
    
    // 모바일만 sessionStorage에 저장
    if (isMobile() && response.data.access_token && response.data.refresh_token) {
      sessionStorage.setItem('access_token', response.data.access_token)
      sessionStorage.setItem('refresh_token', response.data.refresh_token)
      console.log('Mobile: tokens saved to sessionStorage')
    } else if (!isMobile()) {
      console.log('Desktop: using cookies only')
    }
    
    // CSRF 토큰은 모든 환경에서 sessionStorage 사용 (소셜 로그인과 동일)
    if (response.data.csrf_token) {
      sessionStorage.setItem('csrf_token', response.data.csrf_token)
      console.log('[LOGIN] CSRF token saved to sessionStorage')
    }
    
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 로그아웃
export const logout = async () => {
  try {
    const response = await axios.post('/auth/logout')
    
    // 모바일만 sessionStorage 삭제
    if (isMobile()) {
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
      console.log('[LOGOUT] Mobile: tokens removed from sessionStorage')
    }
    
    // CSRF 토큰은 모든 환경에서 삭제
    sessionStorage.removeItem('csrf_token')
    
    return response.data
  } catch (error) {
    // 실패해도 토큰 삭제
    if (isMobile()) {
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
    }
    sessionStorage.removeItem('csrf_token')
    throw error.response?.data || error.message
  }
}

// 토큰 갱신
export const refresh = async () => {
  try {
    const response = await axios.post('/auth/refresh')
    // CSRF 토큰 업데이트
    if (response.data.csrf_token) {
      sessionStorage.setItem('csrf_token', response.data.csrf_token)
    }
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 내 정보 조회
export const getMyInfo = async () => {
  try {
    const response = await axios.get('/member/me')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 내 정보 수정
export const updateMyInfo = async (updateData) => {
  try {
    const response = await axios.put('/member/update_account', updateData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 비밀번호 변경
export const changePassword = async (passwordData) => {
  try {
    const response = await axios.put('/member/change-password', passwordData)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 계정 삭제
export const deleteAccount = async () => {
  try {
    const response = await axios.delete('/member/delete_account')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 프로필 이미지 업로드
export const uploadProfileImage = async (file) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post('/member/upload-profile', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 프로필 이미지 삭제
export const deleteProfileImage = async () => {
  try {
    const response = await axios.delete('/member/delete-profile')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}