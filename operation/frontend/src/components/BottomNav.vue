<template>
  <nav class="fixed bottom-0 left-1/2 transform -translate-x-1/2 z-50 bg-white border border-gray-200 rounded-t-2xl shadow-lg max-w-sm w-full">
    <div class="flex">
      <!-- AI생성 버튼 - 로그인 확인 로직 추가 -->
      <button
        @click="handleGenerateClick"
        class="flex flex-col items-center justify-center flex-1 py-3 transition-colors"
        :class="$route.path === '/generate' ? 'text-blue-600 font-semibold' : 'text-gray-500 hover:text-blue-600'"
      >
        <span class="text-lg mb-1">🧠</span>
        <span class="text-xs">AI생성</span>
      </button>
      
      <router-link 
        to="/" 
        class="flex flex-col items-center justify-center flex-1 py-3 transition-colors"
        :class="$route.path === '/' ? 'text-blue-600 font-semibold' : 'text-gray-500 hover:text-blue-600'"
      >
        <span class="text-lg mb-1">🏠</span>
        <span class="text-xs">홈</span>
      </router-link>
      
      <!-- 로그인 상태에 따른 마지막 버튼 -->
      <router-link 
        v-if="!userStore.isAuthenticated"
        to="/login"
        class="flex flex-col items-center justify-center flex-1 py-3 transition-colors"
        :class="$route.path === '/login' || $route.path === '/signup' ? 'text-blue-600 font-semibold' : 'text-gray-500 hover:text-blue-600'"
      >
        <span class="text-lg mb-1">🔑</span>
        <span class="text-xs">로그인</span>
      </router-link>
      
      <router-link 
        v-else
        to="/mypage"
        class="flex flex-col items-center justify-center flex-1 py-3 transition-colors"
        :class="$route.path === '/mypage' ? 'text-blue-600 font-semibold' : 'text-gray-500 hover:text-blue-600'"
      >
        <span class="text-lg mb-1">👤</span>
        <span class="text-xs">마이페이지</span>
      </router-link>
    </div>
  </nav>
  
  <!-- 로그인 안내 모달 - Teleport로 body에 렌더링 -->
  <Teleport to="body">
    <div v-if="showLoginModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" style="z-index: 9999;">
      <div class="bg-white rounded-2xl max-w-sm w-full p-6">
        <!-- 모달 헤더 -->
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl">🔒</span>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">로그인이 필요합니다</h3>
          <p class="text-sm text-gray-600">
AI 생성 기능은 로그인 후<br />
이용할 수 있습니다.
          </p>
        </div>
        
        <!-- 버튼들 -->
        <div class="space-y-3">
          <router-link 
            to="/login"
            @click="closeLoginModal"
            class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition text-center block"
          >
            로그인하기
          </router-link>
          
          <router-link 
            to="/signup"
            @click="closeLoginModal"
            class="w-full py-3 border border-blue-600 text-blue-600 font-medium rounded-lg hover:bg-blue-50 transition text-center block"
          >
            회원가입
          </router-link>
          
          <button 
            @click="closeLoginModal"
            class="w-full py-2 text-gray-500 text-sm hover:text-gray-700 transition"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, Teleport } from 'vue'
import { useUserStore } from '@/store/userStore'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const showLoginModal = ref(false)

// AI생성 버튼 클릭 처리
const handleGenerateClick = () => {
  if (userStore.isAuthenticated) {
    // 로그인되어 있으면 생성 페이지로 이동
    router.push('/generate')
  } else {
    // 로그인되어 있지 않으면 로그인 모달 표시
    showLoginModal.value = true
  }
}

// 로그인 모달 닫기
const closeLoginModal = () => {
  showLoginModal.value = false
}
</script>