import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Signup from '@/views/Signup.vue'
import MyPage from '@/views/MyPage.vue'
import Generate from '@/views/Generate.vue'
import RecommendedProducts from '@/views/RecommendedProducts.vue'
import MyProducts from '@/views/MyProducts.vue'
import MyReports from '@/views/MyReports.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
  },
  {
    path: '/mypage',
    name: 'MyPage',
    component: MyPage,
    meta: { requiresAuth: true } // 인증 필요
  },
  {
    path: '/generate',
    name: 'Generate',
    component: Generate,
    meta: { requiresAuth: true } // 인증 필요
  },
  {
    path: '/recommended-products',
    name: 'RecommendedProducts',
    component: RecommendedProducts
  },
  {
    path: '/my-products',
    name: 'MyProducts',
    component: MyProducts,
    meta: { requiresAuth: true } // 인증 필요
  },
  {
    path: '/my-reports',
    name: 'MyReports',
    component: MyReports,
    meta: { requiresAuth: true } // 인증 필요
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 인증이 필요한 페이지 보호
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth) {
    // CSRF 토큰이 있으면 인증 상태 확인을 기다림
    const csrfToken = sessionStorage.getItem('csrf_token')
    
    if (csrfToken && !userStore.isAuthenticated) {
      try {
        await userStore.checkAuthStatus()
      } catch (error) {
        // 인증 실패 시 로그인으로 리다이렉트
      }
    }
    
    if (!userStore.isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router