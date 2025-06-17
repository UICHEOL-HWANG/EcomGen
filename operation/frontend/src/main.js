import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import { useUserStore } from './store/userStore'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 앱 시작 시 인증 상태 확인 (CSRF 토큰이 있을 때만)
const userStore = useUserStore()
const csrfToken = localStorage.getItem('csrf_token')
if (csrfToken) {
  userStore.checkAuthStatus().finally(() => {
    app.mount('#app')
  })
} else {
  // CSRF 토큰이 없으면 바로 앱 시작
  app.mount('#app')
}
