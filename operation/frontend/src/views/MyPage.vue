<template>
  <div class="px-4 py-6">
    <!-- 사용자 정보 카드 -->
    <section class="mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <div class="relative w-20 h-20 mx-auto mb-4">
          <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center overflow-hidden">
            <img 
              v-if="userStore.user?.profile_image" 
              :src="userStore.user.profile_image" 
              alt="Profile" 
              class="w-full h-full object-cover"
            />
            <span v-else class="text-2xl">👤</span>
          </div>
          <!-- 프로필 사진 변경 버튼 -->
          <button 
            @click="showProfileImageModal = true"
            class="absolute -bottom-1 -right-1 w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700 transition shadow-md"
          >
            <span class="text-white text-xs">✏️</span>
          </button>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-1">
          {{ userStore.user?.username || userStore.user?.name || '사용자' }}
        </h2>
        <p class="text-gray-600 text-sm mb-4">{{ userStore.user?.email }}</p>
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
            <p class="text-sm text-gray-600">이름 변경</p>
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

      <!-- 내가 검색한 리포트 -->
      <button class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition">
        <div class="flex items-center gap-3">
          <span class="text-lg">📈</span>
          <div class="text-left">
            <h3 class="font-semibold text-gray-900">내가 검색한 리포트</h3>
            <p class="text-sm text-gray-600">AI 에이전트 검색 기록 보기</p>
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

    <!-- 성공 모달 -->
    <Transition name="success-modal">
      <div v-if="showSuccessModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 text-center transform transition-all duration-300">
          <!-- 성공 아이콘 -->
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl">✅</span>
          </div>
          
          <h3 class="text-lg font-bold text-gray-900 mb-2">성공적으로 변경되었습니다!</h3>
          <p class="text-sm text-gray-600 mb-6">
내 정보가 성공적으로 업데이트되었습니다.
          </p>
          
          <button 
            @click="showSuccessModal = false"
            class="w-full py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition"
          >
            확인
          </button>
        </div>
      </div>
    </Transition>

    <!-- 비밀번호 변경 성공 모달 -->
    <Transition name="success-modal">
      <div v-if="showPasswordChangeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-sm w-full p-6 text-center transform transition-all duration-300">
          <!-- 보안 아이콘 -->
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl">🔒</span>
          </div>
          
          <h3 class="text-lg font-bold text-gray-900 mb-2">비밀번호가 변경되었습니다</h3>
          <p class="text-sm text-gray-600 mb-6">
보안상 재로그인이 필요합니다.<br />
로그인 페이지로 이동합니다.
          </p>
          
          <button 
            @click="handleRelogin"
            class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
          >
            로그인 페이지로 이동
          </button>
        </div>
      </div>
    </Transition>

    <!-- 프로필 사진 변경 모달 -->
    <Transition name="success-modal">
      <div v-if="showProfileImageModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl max-w-sm w-full p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-900">프로필 사진 변경</h3>
            <button @click="showProfileImageModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          
          <!-- 현재 프로필 사진 -->
          <div class="text-center mb-6">
            <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3 overflow-hidden">
              <img 
                v-if="userStore.user?.profile_image" 
                :src="userStore.user.profile_image" 
                alt="Profile" 
                class="w-full h-full object-cover"
              />
              <span v-else class="text-3xl">👤</span>
            </div>
            <p class="text-sm text-gray-600">현재 프로필 사진</p>
          </div>
          
          <!-- 옵션 버튼들 -->
          <div class="space-y-3">
            <button 
              @click="handleCameraCapture"
              :disabled="userStore.loading"
              class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              <span>📷</span>
              카메라로 촬영
            </button>
            
            <button 
              @click="handleGallerySelect"
              :disabled="userStore.loading"
              class="w-full py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              <span>🖼️</span>
              갤러리에서 선택
            </button>
            
            <button 
              @click="handleDeleteProfileImage"
              :disabled="userStore.loading || !userStore.user?.profile_image"
              class="w-full py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              <span>🗑️</span>
              프로필 사진 삭제
            </button>
            
            <button 
              @click="showProfileImageModal = false"
              class="w-full py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
            >
              취소
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 카메라 촬영 컴포넌트 -->
    <CameraCapture 
      v-if="showCameraCapture"
      @captured="onCameraCaptured"
      @close="onCameraClose"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, Transition } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { updateMyInfo, changePassword, deleteAccount, uploadProfileImage, deleteProfileImage } from '@/api/auth'
import CameraCapture from '@/components/CameraCapture.vue'

const router = useRouter()
const userStore = useUserStore()

// 모달 상태
const showEditProfile = ref(false)
const showChangePassword = ref(false)
const showDeleteAccount = ref(false)
const showSuccessModal = ref(false)
const showPasswordChangeModal = ref(false)
const showProfileImageModal = ref(false)
const showCameraCapture = ref(false)

// 폼 데이터
const editForm = ref({
  username: ''
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
      username: userStore.user.username || userStore.user.name || ''
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
  
  if (!editForm.value.username) {
    editError.value = '이름을 입력해주세요.'
    return
  }

  try {
    const response = await updateMyInfo(editForm.value)
    
    // 서버 응답이 사용자 정보를 담고 있다면 사용, 그렇지 않으면 폼 데이터 사용
    const updatedUserInfo = response.user || response || editForm.value
    
    // userStore의 사용자 정보를 즉시 업데이트
    userStore.updateUserInfo(updatedUserInfo)
    
    // 폼 데이터도 업데이트된 정보로 동기화
    editForm.value = {
      username: updatedUserInfo.username || updatedUserInfo.name || editForm.value.username
    }
    
    showEditProfile.value = false
    
    // 성공 모달 표시 및 3초 후 자동 닫기
    showSuccessModal.value = true
    setTimeout(() => {
      showSuccessModal.value = false
    }, 3000)
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
    
    // 비밀번호 변경 성공 모달 표시
    showPasswordChangeModal.value = true
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

// 비밀번호 변경 후 재로그인 처리
const handleRelogin = async () => {
  try {
    await userStore.logoutUser()
    router.push('/login')
  } catch (error) {
    console.error('로그아웃 실패:', error)
    // 로그아웃 실패해도 로그인 페이지로 이동
    router.push('/login')
  }
}

// 갤러리에서 사진 선택
const handleGallerySelect = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  
  input.onchange = async (event) => {
    const file = event.target.files[0]
    if (file) {
      await uploadProfileImageFile(file)
    }
  }
  
  input.click()
}

// 카메라로 촬영
const handleCameraCapture = () => {
  showProfileImageModal.value = false
  showCameraCapture.value = true
}

// 카메라에서 사진 촬영 완료
const onCameraCaptured = async (file) => {
  showCameraCapture.value = false
  await uploadProfileImageFile(file)
}

// 카메라 닫기
const onCameraClose = () => {
  showCameraCapture.value = false
  showProfileImageModal.value = true // 프로필 모달로 되돌아가기
}

// 프로필 이미지 업로드
const uploadProfileImageFile = async (file) => {
  try {
    userStore.loading = true
    
    const response = await uploadProfileImage(file)
    
    // 사용자 정보 업데이트
    userStore.updateUserInfo({
      profile_image: response.profile_image_url
    })
    
    showProfileImageModal.value = false
    showSuccessModal.value = true
    setTimeout(() => {
      showSuccessModal.value = false
    }, 3000)
    
  } catch (error) {
    console.error('프로필 사진 업로드 실패:', error)
    alert('프로필 사진 업로드에 실패했습니다.')
  } finally {
    userStore.loading = false
  }
}

// 프로필 사진 삭제
const handleDeleteProfileImage = async () => {
  try {
    userStore.loading = true
    
    await deleteProfileImage()
    
    // 사용자 정보에서 프로필 사진 제거
    userStore.updateUserInfo({
      profile_image: null
    })
    
    showProfileImageModal.value = false
    showSuccessModal.value = true
    setTimeout(() => {
      showSuccessModal.value = false
    }, 3000)
    
  } catch (error) {
    console.error('프로필 사진 삭제 실패:', error)
    alert('프로필 사진 삭제에 실패했습니다.')
  } finally {
    userStore.loading = false
  }
}
</script>

<style scoped>
/* 성공 모달 애니메이션 */
.success-modal-enter-active {
  transition: opacity 0.3s ease;
}

.success-modal-leave-active {
  transition: opacity 0.3s ease;
}

.success-modal-enter-from,
.success-modal-leave-to {
  opacity: 0;
}

.success-modal-enter-to,
.success-modal-leave-from {
  opacity: 1;
}
</style>
