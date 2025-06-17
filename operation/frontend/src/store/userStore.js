import { defineStore } from 'pinia'
import { login, logout, refresh, getMyInfo, signup } from '@/api/auth'

// 모바일 감지 함수
const isMobile = () => {
  return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 하이브리드 저장 전략
const tokenStorage = {
  // 토큰 저장
  setTokens(accessToken, refreshToken, csrfToken) {
    if (isMobile()) {
      // 모바일: sessionStorage 사용
      sessionStorage.setItem('access_token', accessToken)
      sessionStorage.setItem('refresh_token', refreshToken)
      sessionStorage.setItem('csrf_token', csrfToken)
      console.log('[STORAGE] Mobile: tokens saved to sessionStorage')
    } else {
      // 데스크톱: 쿠키만 사용 (sessionStorage 사용 안 함)
      sessionStorage.setItem('csrf_token', csrfToken)  // CSRF만 sessionStorage
      console.log('[STORAGE] Desktop: using cookies only (csrf_token in sessionStorage)')
    }
  },
  
  // 토큰 가져오기
  getTokens() {
    if (isMobile()) {
      return {
        accessToken: sessionStorage.getItem('access_token'),
        refreshToken: sessionStorage.getItem('refresh_token'),
        csrfToken: sessionStorage.getItem('csrf_token')
      }
    } else {
      return {
        accessToken: null,  // 데스크톱은 쿠키에서 가져옴
        refreshToken: null, // 데스크톱은 쿠키에서 가져옴
        csrfToken: sessionStorage.getItem('csrf_token')
      }
    }
  },
  
  // 토큰 삭제
  clearTokens() {
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('csrf_token')
    console.log('[STORAGE] All tokens cleared from sessionStorage')
  },
  
  // CSRF 토큰만 확인 (로그인 상태 확인용)
  hasAuth() {
    return !!sessionStorage.getItem('csrf_token')
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
      // CSRF 토큰이 없으면 로그인되지 않은 상태로 간주
      const csrfToken = localStorage.getItem('csrf_token')
      if (!csrfToken) {
        this.isLoggedIn = false
        this.user = null
        return
      }
      
      try {
        await this.fetchUserInfo()
      } catch (error) {
        // 인증이 없거나 만료된 경우
        this.isLoggedIn = false
        this.user = null
        
        // 모바일만 localStorage 삭제
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
        if (isMobile) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
        localStorage.removeItem('csrf_token')
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