<template>
  <div class="px-4 py-6">
    <!-- 내 활동 요약 -->
    <section class="mb-6">
      <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-100 p-6">
        <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          📊 내 활동 요약
        </h3>
        
        <!-- 로딩 상태 -->
        <div v-if="statsLoading" class="animate-pulse">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="bg-white/70 rounded-lg p-4">
              <div class="h-8 bg-gray-200 rounded mb-2"></div>
              <div class="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
            <div class="bg-white/70 rounded-lg p-4">
              <div class="h-8 bg-gray-200 rounded mb-2"></div>
              <div class="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
          <div class="h-32 bg-white/70 rounded-lg"></div>
        </div>
        
        <!-- 통계 데이터 -->
        <div v-else-if="stats && stats.total_products > 0" class="space-y-4">
          <!-- 주요 지표 -->
          <div class="grid grid-cols-1 gap-4">
            <div class="bg-white/70 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-blue-600">{{ stats.total_products }}</div>
              <div class="text-sm text-gray-600">생성한 상품</div>
            </div>
          </div>
          
          <!-- 카테고리별 분포 -->
          <div v-if="Object.keys(stats.category_breakdown).length > 0" class="bg-white/70 rounded-lg p-4">
            <h4 class="text-sm font-medium text-gray-700 mb-3">카테고리별 분포</h4>
            <div class="space-y-2 max-h-32 overflow-y-auto">
              <div v-for="(count, category) in limitedCategories" :key="category" 
                   class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: getCategoryColor(category) }"></div>
                  <span class="text-sm text-gray-600">{{ category }}</span>
                </div>
                <span class="text-sm font-medium text-gray-900">{{ count }}개</span>
              </div>
              <!-- 더 보기 버튼 -->
              <div v-if="hasMoreCategories" class="pt-2 border-t border-gray-200">
                <button 
                  @click="showAllCategories = !showAllCategories"
                  class="text-sm text-blue-600 hover:text-blue-700 transition"
                >
                  {{ showAllCategories ? '접기' : `+${remainingCategoriesCount}개 더 보기` }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- 간단한 도넛 차트 영역 (나중에 Chart.js로 구현) -->
          <div v-if="Object.keys(stats.category_breakdown).length > 0" class="bg-white/70 rounded-lg p-4">
            <h4 class="text-sm font-medium text-gray-700 mb-3">카테고리 분포 차트</h4>
            <div class="flex justify-center relative">
              <div class="relative">
                <canvas 
                  ref="categoryChart" 
                  width="160" 
                  height="160" 
                  class="max-w-[160px] max-h-[160px] cursor-pointer"
                  @mousemove="handleChartMouseMove"
                  @mouseleave="handleChartMouseLeave"
                ></canvas>
                <!-- 중앙 텍스트 -->
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div class="text-center">
                    <div class="text-lg font-bold text-gray-900">{{ stats.total_products }}</div>
                    <div class="text-xs text-gray-600">총 상품</div>
                  </div>
                </div>
                <!-- 툰팁 -->
                <div 
                  v-if="chartHoverInfo.visible"
                  class="absolute bg-gray-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap pointer-events-none z-10"
                  :style="{ left: chartHoverInfo.x + 'px', top: chartHoverInfo.y + 'px', transform: 'translate(-50%, -120%)' }"
                >
                  {{ chartHoverInfo.category }}: {{ chartHoverInfo.count }}개
                  <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 에러 상태 -->
        <div v-else class="text-center py-6">
          <div class="text-4xl mb-3">📊</div>
          <h4 class="text-md font-semibold text-gray-900 mb-2">아직 집계된 데이터가 없습니다</h4>
          <p class="text-sm text-gray-600 mb-4">AI로 상품을 생성하시면<br />활동 통계를 확인할 수 있어요</p>
          <div class="flex gap-2 justify-center">
            <button 
              @click="goToGenerate"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium flex items-center gap-2"
            >
              <span>✨</span>
              상품 생성하기
            </button>
            <button 
              @click="loadStats"
              class="px-3 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition text-sm"
            >
              새로고침
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 사용자 정보 카드 -->
    <section class="mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <div class="relative w-20 h-20 mx-auto mb-4">
          <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center overflow-hidden">
            <img 
              v-if="userStore.user?.profile_pic" 
              :src="userStore.user.profile_pic" 
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
      <button 
        @click="goToMyProducts"
        class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition"
      >
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
      <button 
        @click="goToMyReports"
        class="w-full bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between hover:bg-gray-50 transition"
      >
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
              autocomplete="name"
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
              autocomplete="current-password"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">새 비밀번호</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              required
              autocomplete="new-password"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">새 비밀번호 확인</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              required
              autocomplete="new-password"
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
                v-if="userStore.user?.profile_pic" 
                :src="userStore.user.profile_pic" 
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
              :disabled="userStore.loading || !userStore.user?.profile_pic"
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
import { ref, onMounted, Transition, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { updateMyInfo, changePassword, deleteAccount, uploadProfileImage, deleteProfileImage } from '@/api/auth'
import { getMyProductsStats } from '@/api/products'
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

// 카테고리 리스트 제한 및 더 보기 기능
const showAllCategories = ref(false)
const maxDisplayCategories = 6 // 최대 표시 카테고리 수

// 차트 애니메이션 관련 상태 추가
const chartAnimation = ref({
  progress: 0,
  duration: 1000, // 1초 애니메이션
  isAnimating: false
})

// 통계 관련 상태
const stats = ref(null)
const statsLoading = ref(false)
const categoryChart = ref(null)
const chartHoverInfo = ref({ visible: false, x: 0, y: 0, category: '', count: 0 })
const chartSlices = ref([])

// 카테고리 리스트 계산된 속성
const limitedCategories = computed(() => {
  if (!stats.value?.category_breakdown) return {}
  
  const categories = Object.entries(stats.value.category_breakdown)
  
  if (showAllCategories.value || categories.length <= maxDisplayCategories) {
    return stats.value.category_breakdown
  }
  
  // 개수로 정렬하여 상위 N개만 표시
  const sortedCategories = categories.sort((a, b) => b[1] - a[1])
  const limitedEntries = sortedCategories.slice(0, maxDisplayCategories)
  
  return Object.fromEntries(limitedEntries)
})

// 더 보기 버튼 표시 여부
const hasMoreCategories = computed(() => {
  if (!stats.value?.category_breakdown) return false
  return Object.keys(stats.value.category_breakdown).length > maxDisplayCategories
})

// 남은 카테고리 수
const remainingCategoriesCount = computed(() => {
  if (!stats.value?.category_breakdown) return 0
  return Math.max(0, Object.keys(stats.value.category_breakdown).length - maxDisplayCategories)
})

// 컴포넌트 마운트 시 사용자 정보로 폼 초기화
onMounted(async () => {
  if (userStore.user) {
    editForm.value = {
      username: userStore.user.username || userStore.user.name || ''
    }
  }
  
  // 통계 데이터 로드
  await loadStats()
  
  // 차트 강제 다시 그리기 (디버그용)
  setTimeout(() => {
    if (stats.value?.category_breakdown && Object.keys(stats.value.category_breakdown).length > 0) {
      console.log('차트 강제 다시 그리기 시도')
      drawChart()
    }
  }, 500)
})

// 통계 데이터 로드
const loadStats = async () => {
  try {
    statsLoading.value = true
    const response = await getMyProductsStats()
    stats.value = response
    
    // 차트 그리기 (다음 틱에 실행)
    await nextTick()
    if (Object.keys(response.category_breakdown).length > 0) {
      drawChart()
    }
  } catch (error) {
    console.error('통계 로드 실패:', error)
    stats.value = null
  } finally {
    statsLoading.value = false
  }
}

// 카테고리별 색상 매핑 (동적 색상 생성)
const categoryColorMap = ref({})

const getCategoryColor = (category) => {
  // 이미 색상이 할당된 카테고리면 기존 색상 반환
  if (categoryColorMap.value[category]) {
    return categoryColorMap.value[category]
  }
  
  // 미리 정의된 좋은 색상 팔레트
  const colorPalette = [
    '#3B82F6', // 파란색
    '#10B981', // 초록색
    '#F59E0B', // 주황색
    '#EF4444', // 빨간색
    '#8B5CF6', // 보라색
    '#06B6D4', // 청록색
    '#84CC16', // 라임색
    '#F97316', // 오렌지색
    '#EC4899', // 핑크색
    '#14B8A6', // 틸색
    '#8B5A2B', // 갈색
    '#6366F1', // 인디고색
    '#DC2626', // 진한 빨간색
    '#059669', // 진한 초록색
    '#7C3AED', // 진한 보라색
    '#0891B2', // 진한 청록색
  ]
  
  // 기존에 사용된 색상들 추적
  const usedColors = Object.values(categoryColorMap.value)
  
  // 아직 사용되지 않은 색상 찾기
  let availableColor = colorPalette.find(color => !usedColors.includes(color))
  
  // 모든 팔레트 색상이 사용되었다면 랜덤 색상 생성
  if (!availableColor) {
    const hue = Math.floor(Math.random() * 360)
    const saturation = 60 + Math.floor(Math.random() * 20) // 60-80%
    const lightness = 45 + Math.floor(Math.random() * 15) // 45-60%
    availableColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`
  }
  
  // 카테고리에 색상 할당
  categoryColorMap.value[category] = availableColor
  return availableColor
}

// 간단한 도넛 차트 그리기 (부드러운 애니메이션 적용)
const drawChart = () => {
  if (!categoryChart.value || !stats.value?.category_breakdown) {
    console.log('차트 그리기 조건 불충족:', {
      canvas: !!categoryChart.value,
      data: !!stats.value?.category_breakdown
    })
    return
  }
  
  // 애니메이션 시작
  startChartAnimation()
}

// 차트 애니메이션 시작
const startChartAnimation = () => {
  chartAnimation.value.progress = 0
  chartAnimation.value.isAnimating = true
  
  const startTime = performance.now()
  
  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / chartAnimation.value.duration, 1)
    
    // Ease-out 애니메이션 커브 (부드럽게 끝남)
    chartAnimation.value.progress = 1 - Math.pow(1 - progress, 3)
    
    // 차트 그리기
    drawAnimatedChart()
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      chartAnimation.value.isAnimating = false
      // 애니메이션 완료 후 마우스 이벤트를 위한 최종 슬라이스 정보 생성
      generateSliceInfo()
    }
  }
  
  requestAnimationFrame(animate)
}

// 애니메이션이 적용된 차트 그리기
const drawAnimatedChart = () => {
  const canvas = categoryChart.value
  const ctx = canvas.getContext('2d')
  
  // 고정된 캔버스 크기 사용
  canvas.width = 160
  canvas.height = 160
  
  const centerX = 80
  const centerY = 80
  const outerRadius = 70
  const innerRadius = 35
  
  // 캔버스 초기화
  ctx.clearRect(0, 0, 160, 160)
  
  const categories = Object.entries(stats.value.category_breakdown)
  
  if (categories.length === 0) {
    ctx.beginPath()
    ctx.arc(centerX, centerY, outerRadius, 0, 2 * Math.PI)
    ctx.strokeStyle = '#e5e7eb'
    ctx.lineWidth = 2
    ctx.stroke()
    return
  }
  
  const total = Object.values(stats.value.category_breakdown).reduce((sum, count) => sum + count, 0)
  
  let currentAngle = -Math.PI / 2 // 12시 방향부터 시작
  
  categories.forEach(([category, count], index) => {
    const sliceAngle = (count / total) * 2 * Math.PI
    
    // 애니메이션 지연: 각 슬라이스마다 순차적으로 나타나게
    const animationDelay = (index / categories.length) * 0.4 // 40% 지연
    const sliceProgress = Math.max(0, Math.min(1, (chartAnimation.value.progress - animationDelay) / (1 - animationDelay)))
    const animatedSliceAngle = sliceAngle * sliceProgress
    
    // 최소 각도 보장 (작은 조각도 호버 가능하도록)
    const minAngle = 0.15
    const adjustedSliceAngle = animatedSliceAngle > 0 ? Math.max(animatedSliceAngle, Math.min(minAngle, sliceAngle)) : 0
    
    if (adjustedSliceAngle > 0) {
      // 도넛 슬라이스 그리기
      ctx.beginPath()
      ctx.arc(centerX, centerY, outerRadius, currentAngle, currentAngle + adjustedSliceAngle)
      ctx.arc(centerX, centerY, innerRadius, currentAngle + adjustedSliceAngle, currentAngle, true)
      ctx.closePath()
      
      // 색상 설정 (애니메이션 진행률에 따른 투명도 조절)
      const color = getCategoryColor(category)
      const alpha = Math.min(1, sliceProgress + 0.2) // 최소 20% 투명도
      
      // 색상에 알파 값 추가
      const hex = color.replace('#', '')
      const r = parseInt(hex.substring(0, 2), 16)
      const g = parseInt(hex.substring(2, 4), 16)
      const b = parseInt(hex.substring(4, 6), 16)
      
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`
      ctx.fill()
      
      // 테두리
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.stroke()
    }
    
    currentAngle += sliceAngle // 전체 각도로 진행 (다음 슬라이스 위치 계산용)
  })
}

// 애니메이션 완료 후 마우스 호버를 위한 슬라이스 정보 생성
const generateSliceInfo = () => {
  if (!stats.value?.category_breakdown) return
  
  const categories = Object.entries(stats.value.category_breakdown)
  const total = Object.values(stats.value.category_breakdown).reduce((sum, count) => sum + count, 0)
  
  let currentAngle = -Math.PI / 2
  chartSlices.value = []
  
  categories.forEach(([category, count]) => {
    const sliceAngle = (count / total) * 2 * Math.PI
    const minAngle = 0.15
    const adjustedSliceAngle = Math.max(sliceAngle, minAngle)
    
    // 각도 정규화
    let normalizedStart = currentAngle
    if (normalizedStart < 0) normalizedStart += 2 * Math.PI
    
    let normalizedEnd = currentAngle + adjustedSliceAngle
    if (normalizedEnd < 0) normalizedEnd += 2 * Math.PI
    
    chartSlices.value.push({
      category,
      count,
      startAngle: normalizedStart,
      endAngle: normalizedEnd,
      centerX: 80,
      centerY: 80,
      outerRadius: 70,
      innerRadius: 35
    })
    
    currentAngle += adjustedSliceAngle
  })
  
  console.log('차트 애니메이션 완료 및 슬라이스 정보 생성 완료')
}

// 차트 마우스 이벤트 처리
const handleChartMouseMove = (event) => {
  if (!chartSlices.value.length) return
  
  const canvas = categoryChart.value
  const rect = canvas.getBoundingClientRect()
  
  // 캔버스 상에서의 마우스 위치 (스케일링 고려)
  const scaleX = 160 / rect.width
  const scaleY = 160 / rect.height
  const x = (event.clientX - rect.left) * scaleX
  const y = (event.clientY - rect.top) * scaleY
  
  // 차트 중심에서의 거리와 각도 계산
  const dx = x - 80
  const dy = y - 80
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  // 각도 계산: Math.atan2로 기본 각도 계산 후 정규화
  let angle = Math.atan2(dy, dx)
  if (angle < 0) angle += 2 * Math.PI
  
  console.log(`마우스: (${x.toFixed(1)}, ${y.toFixed(1)}), 거리: ${distance.toFixed(1)}, 각도: ${(angle * 180 / Math.PI).toFixed(1)}도`)
  
  // 호버된 슬라이스 찾기
  const hoveredSlice = chartSlices.value.find(slice => {
    const isInRange = distance >= slice.innerRadius && distance <= slice.outerRadius
    let isInAngle = false
    
    // 각도 범위 검사
    if (slice.endAngle > slice.startAngle) {
      // 일반적인 경우
      isInAngle = angle >= slice.startAngle && angle <= slice.endAngle
    } else {
      // 2π를 넘는 경우 (0도 근처에서 끊긴 경우)
      isInAngle = angle >= slice.startAngle || angle <= slice.endAngle
    }
    
    if (isInRange && isInAngle) {
      console.log(`호버 감지! 카테고리: ${slice.category}, 시작: ${(slice.startAngle * 180 / Math.PI).toFixed(1)}도, 끝: ${(slice.endAngle * 180 / Math.PI).toFixed(1)}도`)
    }
    
    return isInRange && isInAngle
  })
  
  if (hoveredSlice) {
    chartHoverInfo.value = {
      visible: true,
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      category: hoveredSlice.category,
      count: hoveredSlice.count
    }
  } else {
    chartHoverInfo.value.visible = false
  }
}

// 차트 마우스 떠날 때 처리
const handleChartMouseLeave = () => {
  chartHoverInfo.value.visible = false
}

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

// 내가 만든 상품 페이지로 이동
const goToMyProducts = () => {
  router.push('/my-products')
}

// 내가 검색한 리포트 페이지로 이동
const goToMyReports = () => {
  router.push('/my-reports')
}

// 상품 생성 페이지로 이동
const goToGenerate = () => {
  router.push('/generate')
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
    
    // 사용자 정보 새로 가져오기 (데이터베이스에서 최신 정보 동기화)
    await userStore.fetchUserInfo()
    
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
    
    // 사용자 정보 새로 가져오기 (데이터베이스에서 최신 정보 동기화)
    await userStore.fetchUserInfo()
    
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
