<template>
  <nav class="fixed bottom-0 left-1/2 transform -translate-x-1/2 z-50 bg-white border border-gray-200 rounded-t-2xl shadow-lg max-w-sm w-full">
    <div class="flex">
      <router-link
        to="/generate"
        class="flex flex-col items-center justify-center flex-1 py-3 transition-colors"
        :class="$route.path === '/generate' ? 'text-blue-600 font-semibold' : 'text-gray-500 hover:text-blue-600'"
      >
        <span class="text-lg mb-1">🧠</span>
        <span class="text-xs">AI생성</span>
      </router-link>
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
</template>

<script setup>
import { useUserStore } from '@/store/userStore'

const userStore = useUserStore()
</script>