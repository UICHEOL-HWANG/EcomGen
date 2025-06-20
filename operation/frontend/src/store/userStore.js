import { defineStore } from 'pinia'
import { login, logout, refresh, getMyInfo, signup } from '@/api/auth'

// 모바일 감지 함수
const isMobile = () => {
  return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 토큰 관리를 위한 간단한 저장소
const tokenStorage = {
  // 토큰 삭제
  clearTokens() {
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('csrf_token')
    console.log('[STORAGE] All tokens cleared from sessionStorage')
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => state.isLoggedIn && !!state.user,
    userInfo: (state) => state.user,
    userName: (state) => state.user?.username || state.user?.name || '',
    userEmail: (state) => state.user?.email || ''
  },
  
  actions: {
    // 회원가입
    async signupUser(userData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await signup(userData)
        return response
      } catch (error) {
        this.error = error.detail || '회원가입에 실패했습니다.'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 로그인
    async loginUser(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const response = await login(credentials)
        
        // 로그인 성공 후 사용자 정보 가져오기
        await this.fetchUserInfo()
        
        this.isLoggedIn = true
        return true
      } catch (error) {
        this.error = error.detail || '로그인에 실패했습니다.'
        this.isLoggedIn = false
        this.user = null
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 로그아웃
    async logoutUser() {
      this.loading = true
      this.error = null
      
      try {
        await logout()
      } catch (error) {
        console.error('Logout failed:', error)
        // 로그아웃은 실패해도 로컬 상태는 초기화
      } finally {
        this.isLoggedIn = false
        this.user = null
        this.loading = false
        tokenStorage.clearTokens()
      }
    },
    
    // 사용자 정보 가져오기
    async fetchUserInfo() {
      this.loading = true
      this.error = null
      
      try {
        const userInfo = await getMyInfo()
        this.user = userInfo
        this.isLoggedIn = true
        return userInfo
      } catch (error) {
        this.error = error.detail || '사용자 정보를 가져오는데 실패했습니다.'
        this.isLoggedIn = false
        this.user = null
        throw error
      } finally {
        this.loading = false
      }
    },
    

    
    // 인증 상태 확인
    async checkAuthStatus() {
      try {
        await this.fetchUserInfo()
      } catch (error) {
        // 인증이 없거나 만료된 경우
        this.isLoggedIn = false
        this.user = null
        tokenStorage.clearTokens()
      }
    },
    
    // 토큰 갱신
    async refreshToken() {
      try {
        await refresh()
      } catch (error) {
        console.error('Token refresh failed:', error)
        this.isLoggedIn = false
        this.user = null
        throw error
      }
    },
    
    // 사용자 정보 업데이트 (로컬 상태 직접 업데이트)
    updateUserInfo(updatedInfo) {
      if (this.user) {
        this.user = { ...this.user, ...updatedInfo }
      }
    },
    
    // 에러 초기화
    clearError() {
      this.error = null
    }
  }
})