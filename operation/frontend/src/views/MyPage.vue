<template>
  <div class="px-4 py-6">
    <!-- 사용자 정보 카드 -->
    <section class="mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="text-2xl">👤</span>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-1">
          {{ userStore.user?.username || userStore.user?.name || '사용자' }}
        </h2>
        <p class="text-gray-600 text-sm mb-4">{{ userStore.user?.email }}</p>
        <div class="flex items-center justify-center gap-2">
          <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
            ✅ 인증됨
          </span>
        </div>
      </div>
    </section>

    <!-- 메뉴 리스트 -->
    <section class="space-y-3">
      <!-- 내 정보 수정 -->
      <button 
        @click="showEditProfile = true"
        class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition"
      >
        <div class="flex items-center gap-3">
          <span class="text-lg">✏️</span>
          <div class="text-left">
            <h3 class="font-semibold text-gray-900">내 정보 수정</h3>
            <p class="text-sm text-gray-600">이름, 이메일 변경</p>
          </div>
        </div>
        <span class="text-gray-400">›</span>
      </button>

      <!-- 비밀번호 변경 -->
      <button 
        @click="showChangePassword = true"
        class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition"
      >
        <div class="flex items-center gap-3">
          <span class="text-lg">🔒</span>
          <div class="text-left">
            <h3 class="font-semibold text-gray-900">비밀번호 변경</h3>
            <p class="text-sm text-gray-600">계정 보안 강화</p>
          </div>
        </div>
        <span class="text-gray-400">›</span>
      </button>

      <!-- 내가 만든 상품 -->
      <button class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition">
        <div class="flex items-center gap-3">
          <span class="text-lg">📦</span>
          <div class="text-left">
            <h3 class="font-semibold text-gray-900">내가 만든 상품</h3>
            <p class="text-sm text-gray-600">생성한 상품 목록 보기</p>
          </div>
        </div>
        <span class="text-gray-400">›</span>
      </button>

      <!-- 설정 -->
      <button class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition">
        <div class="flex items-center gap-3">
          <span class="text-lg">⚙️</span>
          <div class="text-left">
            <h3 class="font-semibold text-gray-900">설정</h3>
            <p class="text-sm text-gray-600">알림, 개인정보 설정</p>
          </div>
        </div>
        <span class="text-gray-400">›</span>
      </button>

      <!-- 로그아웃 -->
      <button 
        @click="handleLogout"
        :disabled="userStore.loading"
        class="w-full bg-red-50 rounded-xl border border-red-200 p-4 flex items-center justify-between hover:bg-red-100 transition"
      >
        <div class="flex items-center gap-3">
          <span class="text-lg">🚪</span>
          <div class="text-left">
            <h3 class="font-semibold text-red-600">로그아웃</h3>
            <p class="text-sm text-red-500">계정에서 로그아웃</p>
          </div>
        </div>
        <span class="text-red-400">{{ userStore.loading ? '...' : '›' }}</span>
      </button>

      <!-- 계정 삭제 -->
      <button 
        @click="showDeleteAccount = true"
        class="w-full bg-gray-50 rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-100 transition"
      >
        <div class="flex items-center gap-3">
          <span class="text-lg">🗑️</span>
          <div class="text-left">
            <h3 class="font-semibold text-gray-700">계정 삭제</h3>
            <p class="text-sm text-gray-500">계정을 영구적으로 삭제</p>
          </div>
        </div>
        <span class="text-gray-400">›</span>
      </button>
    </section>

    <!-- 내 정보 수정 모달 -->
    <div v-if="showEditProfile" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-sm w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">내 정보 수정</h3>
          <button @click="showEditProfile = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        
        <form @submit.prevent="handleUpdateProfile" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">이름</label>
            <input
              v-model="editForm.username"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">이메일</label>
            <input
              v-model="editForm.email"
              type="email"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          <div v-if="editError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ editError }}</p>
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              @click="showEditProfile = false"
              class="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
            >
              취소
            </button>
            <button
              type="submit"
              :disabled="userStore.loading"
              class="flex-1 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              {{ userStore.loading ? '저장 중...' : '저장' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 비밀번호 변경 모달 -->
    <div v-if="showChangePassword" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-sm w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">비밀번호 변경</h3>
          <button @click="showChangePassword = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        
        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">현재 비밀번호</label>
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">새 비밀번호</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">새 비밀번호 확인</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          <div v-if="passwordError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{{ passwordError }}</p>
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              @click="showChangePassword = false"
              class="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
            >
              취소
            </button>
            <button
              type="submit"
              :disabled="userStore.loading"
              class="flex-1 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              {{ userStore.loading ? '변경 중...' : '변경' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 계정 삭제 확인 모달 -->
    <div v-if="showDeleteAccount" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-sm w-full p-6">
        <div class="text-center mb-4">
          <span class="text-4xl mb-2 block">⚠️</span>
          <h3 class="text-lg font-bold text-gray-900 mb-2">계정을 삭제하시겠습니까?</h3>
          <p class="text-sm text-gray-600">이 작업은 되돌릴 수 없으며, 모든 데이터가 영구적으로 삭제됩니다.</p>
        </div>

        <div v-if="deleteError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ deleteError }}</p>
        </div>

        <div class="flex gap-3">
          <button
            @click="showDeleteAccount = false"
            class="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
          >
            취소
          </button>
          <button
            @click="handleDeleteAccount"
            :disabled="userStore.loading"
            class="flex-1 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition"
          >
            {{ userStore.loading ? '삭제 중...' : '삭제' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { updateMyInfo, changePassword, deleteAccount } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

// 모달 상태
const showEditProfile = ref(false)
const showChangePassword = ref(false)
const showDeleteAccount = ref(false)

// 폼 데이터
const editForm = ref({
  username: '',
  email: ''
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 에러 상태
const editError = ref('')
const passwordError = ref('')
const deleteError = ref('')

// 컴포넌트 마운트 시 사용자 정보로 폼 초기화
onMounted(() => {
  if (userStore.user) {
    editForm.value = {
      username: userStore.user.username || userStore.user.name || '',
      email: userStore.user.email || ''
    }
  }
})

// 로그아웃 처리
const handleLogout = async () => {
  try {
    await userStore.logoutUser()
    router.push('/')
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

// 내 정보 수정
const handleUpdateProfile = async () => {
  editError.value = ''
  
  if (!editForm.value.username || !editForm.value.email) {
    editError.value = '모든 필드를 입력해주세요.'
    return
  }

  try {
    await updateMyInfo(editForm.value)
    await userStore.fetchUserInfo() // 사용자 정보 새로고침
    showEditProfile.value = false
  } catch (error) {
    editError.value = error.detail || '정보 수정에 실패했습니다.'
  }
}

// 비밀번호 변경
const handleChangePassword = async () => {
  passwordError.value = ''
  
  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    passwordError.value = '모든 필드를 입력해주세요.'
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }

  if (passwordForm.value.newPassword.length < 8) {
    passwordError.value = '새 비밀번호는 8자 이상이어야 합니다.'
    return
  }

  try {
    await changePassword({
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword,
      confirm_password: passwordForm.value.confirmPassword
    })
    
    showChangePassword.value = false
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    passwordError.value = error.detail || '비밀번호 변경에 실패했습니다.'
  }
}

// 계정 삭제
const handleDeleteAccount = async () => {
  deleteError.value = ''
  
  try {
    await deleteAccount()
    router.push('/')
  } catch (error) {
    deleteError.value = error.detail || '계정 삭제에 실패했습니다.'
  }
}
</script>
