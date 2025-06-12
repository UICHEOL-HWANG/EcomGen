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

// 앱 시작 시 인증 상태 확인
const userStore = useUserStore()
userStore.checkAuthStatus().finally(() => {
  app.mount('#app')
})
