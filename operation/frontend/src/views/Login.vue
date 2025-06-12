<template>
  <div class="px-4 py-6">
    <!-- 로그인 헤더 -->
    <section class="text-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">로그인</h1>
      <p class="text-gray-600 text-sm">Shoplingo에 오신 것을 환영합니다</p>
    </section>

    <!-- 로그인 폼 -->
    <section class="mb-6">
      <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- 이메일 입력 -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">이메일</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="이메일을 입력하세요"
          />
        </div>

        <!-- 비밀번호 입력 -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">비밀번호</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="비밀번호를 입력하세요"
          />
        </div>

        <!-- 로그인 버튼 -->
        <button
          type="submit"
          class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
          :disabled="userStore.loading"
        >
          {{ userStore.loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <!-- 에러 메시지 -->
      <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-sm text-red-600">{{ errorMessage }}</p>
      </div>

      <!-- 비밀번호 찾기 -->
      <div class="text-center mt-4">
        <a href="#" class="text-sm text-blue-600 hover:text-blue-700">비밀번호를 잊으셨나요?</a>
      </div>
    </section>

    <!-- 구분선 -->
    <div class="relative mb-6">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-300"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-2 bg-white text-gray-500">또는</span>
      </div>
    </div>

    <!-- 소셜 로그인 -->
    <section class="space-y-3 mb-6">
      <button class="w-full flex items-center justify-center gap-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
        <span class="text-lg">🟡</span>
        <span class="font-medium text-gray-700">카카오로 계속하기</span>
      </button>
      
      <button class="w-full flex items-center justify-center gap-3 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
        <span class="text-lg">🔵</span>
        <span class="font-medium text-gray-700">구글로 계속하기</span>
      </button>
    </section>

    <!-- 회원가입 링크 -->
    <section class="text-center">
      <p class="text-sm text-gray-600">
        아직 계정이 없으신가요? 
        <router-link to="/signup" class="text-blue-600 hover:text-blue-700 font-medium">회원가입</router-link>
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  email: '',
  password: ''
})

const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  
  if (!form.value.email || !form.value.password) {
    errorMessage.value = '로그인 정보를 모두 입력해주세요.'
    return
  }
  
  try {
    await userStore.loginUser({
      email: form.value.email,
      password: form.value.password
    })
    
    // 로그인 성공 시 홈으로 이동
    router.push('/')
  } catch (error) {
    errorMessage.value = userStore.error || '로그인에 실패했습니다.'
  }
}
</script>
