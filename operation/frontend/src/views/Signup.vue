<template>
  <div class="px-4 py-6">
    <!-- 회원가입 헤더 -->
    <section class="text-center mb-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">회원가입</h1>
      <p class="text-gray-600 text-sm">새로운 계정을 만들어보세요</p>
    </section>

    <!-- 회원가입 폼 -->
    <section class="mb-6">
      <form @submit.prevent="handleSignup" class="space-y-4">
        <!-- 이름 입력 -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2">이름</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            autocomplete="username"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="이름을 입력하세요"
          />
        </div>

        <!-- 이메일 입력 -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">이메일</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            autocomplete="email"
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
            autocomplete="new-password"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="비밀번호를 입력하세요 (8자 이상)"
          />
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">비밀번호 확인</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            required
            autocomplete="new-password"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="비밀번호를 다시 입력하세요"
          />
        </div>

        <!-- 약관 동의 -->
        <div class="flex items-start gap-3">
          <input
            id="terms"
            v-model="form.agreeTerms"
            type="checkbox"
            required
            class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="terms" class="text-sm text-gray-700 leading-relaxed">
            <span class="text-blue-600 hover:text-blue-700">이용약관</span> 및 
            <span class="text-blue-600 hover:text-blue-700">개인정보처리방침</span>에 동의합니다.
          </label>
        </div>

        <!-- 회원가입 버튼 -->
        <button
          type="submit"
          class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
          :disabled="userStore.loading"
        >
          {{ userStore.loading ? '계정 생성 중...' : '계정 만들기' }}
        </button>
      </form>
      
      <!-- 성공/에러 메시지 -->
      <div v-if="successMessage" class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-sm text-green-600">{{ successMessage }}</p>
      </div>
      
      <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-sm text-red-600">{{ errorMessage }}</p>
      </div>
    </section>



    <!-- 로그인 링크 -->
    <section class="text-center">
      <p class="text-sm text-gray-600">
        이미 계정이 있으신가요? 
        <router-link to="/login" class="text-blue-600 hover:text-blue-700 font-medium">로그인</router-link>
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
  username: '', // backend에서 name 대신 username 사용
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

const errorMessage = ref('')
const successMessage = ref('')

const handleSignup = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  // 클라이언트 측 검증
  if (!form.value.username || !form.value.email || !form.value.password || !form.value.confirmPassword) {
    errorMessage.value = '모든 필드를 입력해주세요.'
    return
  }
  
  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  if (form.value.password.length < 8) {
    errorMessage.value = '비밀번호는 8자 이상이어야 합니다.'
    return
  }
  
  if (!form.value.agreeTerms) {
    errorMessage.value = '이용약관에 동의해주세요.'
    return
  }

  try {
    await userStore.signupUser({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })
    
    successMessage.value = '회원가입이 성공했습니다! 로그인 페이지로 이동합니다.'
    
    // 2초 후 로그인 페이지로 이동
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (error) {
    errorMessage.value = userStore.error || '회원가입에 실패했습니다.'
  }
}
</script>
