import { defineStore } from 'pinia'
import { login, logout, refresh, getMyInfo, signup } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => state.isLoggedIn && !!state.user,
    userInfo: (state) => state.user
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
        await login(credentials)
        
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
      try {
        await this.fetchUserInfo()
      } catch (error) {
        // 인증이 없거나 만료된 경우
        this.isLoggedIn = false
        this.user = null
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
    
    // 에러 초기화
    clearError() {
      this.error = null
    }
  }
})