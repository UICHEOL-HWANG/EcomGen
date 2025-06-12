import axios from './axios'

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
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 로그아웃
export const logout = async () => {
  try {
    const response = await axios.post('/auth/logout')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 토큰 갱신
export const refresh = async () => {
  try {
    const response = await axios.post('/auth/refresh')
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