<template>
  <div class="px-4 pt-2 pb-6">
    <!-- 로그인 상태에 따른 Hero Section -->
    <section class="text-center mb-8">
      <!-- 로그인하지 않은 경우 -->
      <div v-if="!userStore.isAuthenticated">
        <h1 class="text-2xl font-bold leading-tight mb-4 text-gray-900">
          🛍️ 상품 설명, 이미지까지<br />한 번에 자동 생성하세요
        </h1>
        <p class="text-gray-600 text-sm mb-6 leading-relaxed">
          상품명만 입력하면 AI가 자동으로 이미지를 생성하고<br />
          마케팅 설명까지 완성해줍니다.
        </p>
        <div class="flex gap-3 justify-center">
          <button class="px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition flex-1 max-w-[120px]">
            시작하기
          </button>
          <router-link 
            to="/login" 
            class="px-6 py-3 rounded-lg border border-blue-600 text-blue-600 font-medium hover:bg-blue-50 transition flex-1 max-w-[120px] text-center"
          >
            로그인
          </router-link>
        </div>
      </div>
      
      <!-- 로그인한 경우 -->
      <div v-else>
        <h1 class="text-2xl font-bold leading-tight mb-2 text-gray-900">
          안녕하세요, {{ userStore.user?.username || userStore.user?.name }}님! 👋
        </h1>
        <p class="text-gray-600 text-sm mb-6 leading-relaxed">
          오늘도 멋진 상품을 만들어보세요
        </p>
        <div class="flex gap-3 justify-center">
          <router-link
            to="/generate"
            class="px-4 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition text-center"
          >
            상품 생성하기
          </router-link>
          <button 
            @click="handleLogout"
            :disabled="userStore.loading"
            class="px-4 py-3 rounded-lg border border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition"
          >
            {{ userStore.loading ? '로그아웃 중...' : '로그아웃' }}
          </button>
        </div>
      </div>
    </section>

    <!-- 다른 회원들의 추천 상품 -->
    <section class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-gray-900">🔥 다른 회원들의 추천 상품</h2>
        <button 
          @click="goToRecommendedProducts"
          class="text-sm text-blue-600 hover:text-blue-700"
        >
          더보기
        </button>
      </div>
      
      <!-- 스라이드 컨테이너 -->
      <div class="overflow-x-auto scrollbar-hide">
        <div class="flex gap-3 pb-2" style="width: max-content;">
          <div 
            v-for="product in recommendedProducts" 
            :key="product.id"
            class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex-shrink-0 w-40"
          >
            <!-- 상품 이미지 -->
            <div class="relative">
              <div class="w-full h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-xl flex items-center justify-center">
                <span class="text-3xl">{{ product.emoji }}</span>
              </div>
              <div class="absolute top-2 right-2 bg-white rounded-full px-2 py-1 text-xs text-gray-600 shadow-sm">
                AI 생성
              </div>
            </div>
            
            <!-- 상품 정보 -->
            <div class="p-3">
              <h3 class="font-semibold text-sm text-gray-900 mb-1 line-clamp-2">{{ product.name }}</h3>
              <p class="text-xs text-gray-500 mb-2">{{ product.user }}님이 생성</p>
              <div class="flex items-center justify-end">
                <span class="text-sm font-bold text-blue-600">{{ product.price }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI 리포트 섹션 -->
    <section class="mb-8">
      <div class="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl border border-purple-100 p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <span class="text-xl text-white">📊</span>
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">AI 리포트</h2>
              <p class="text-sm text-gray-600">시장 동향과 인사이트 분석</p>
            </div>
          </div>
        </div>
        
        <!-- 리포트 기능 카드들 -->
        <div class="grid grid-cols-2 gap-3 mb-4">
          <button 
            @click="goToReports('trends')"
            class="bg-white/70 hover:bg-white rounded-xl p-4 text-left transition-all hover:shadow-sm"
          >
            <div class="text-lg mb-2">📈</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">트렌드 분석</h3>
            <p class="text-xs text-gray-600">인기 카테고리와 키워드</p>
          </button>
          
          <button 
            @click="goToReports('performance')"
            class="bg-white/70 hover:bg-white rounded-xl p-4 text-left transition-all hover:shadow-sm"
          >
            <div class="text-lg mb-2">🏆</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">성과 분석</h3>
            <p class="text-xs text-gray-600">내 상품 성과 리포트</p>
          </button>
          
          <button 
            @click="goToReports('market')"
            class="bg-white/70 hover:bg-white rounded-xl p-4 text-left transition-all hover:shadow-sm"
          >
            <div class="text-lg mb-2">🌐</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">시장 리서치</h3>
            <p class="text-xs text-gray-600">경쟁 대비 분석</p>
          </button>
          
          <button 
            @click="goToReports('insights')"
            class="bg-white/70 hover:bg-white rounded-xl p-4 text-left transition-all hover:shadow-sm"
          >
            <div class="text-lg mb-2">💡</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">인사이트</h3>
            <p class="text-xs text-gray-600">AI 추천 전략</p>
          </button>
        </div>
        
        <!-- AI 에이전트 검색 버튼 -->
        <button 
          @click="userStore.isAuthenticated ? showReportModal = true : showLoginModal = true"
          class="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium rounded-xl hover:from-purple-600 hover:to-blue-600 transition-all"
        >
          🔍 AI 에이전트에게 검색하기
        </button>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="space-y-3">
      <div class="bg-blue-50 p-4 rounded-lg border border-blue-100">
        <div class="flex items-start gap-3">
          <span class="text-xl">⚡</span>
          <div>
            <h2 class="font-semibold text-gray-900 mb-1">빠른 시작</h2>
            <p class="text-sm text-gray-600">회원가입 하고 상품명만 입력해 바로 생성할 수 있어요.</p>
          </div>
        </div>
      </div>
      
      <div class="bg-yellow-50 p-4 rounded-lg border border-yellow-100">
        <div class="flex items-start gap-3">
          <span class="text-xl">🎨</span>
          <div>
            <h2 class="font-semibold text-gray-900 mb-1">이미지 자동 생성</h2>
            <p class="text-sm text-gray-600">AI가 스타일, 카테고리에 맞는 이미지를 자동 생성해줍니다.</p>
          </div>
        </div>
      </div>
      
      <div class="bg-green-50 p-4 rounded-lg border border-green-100">
        <div class="flex items-start gap-3">
          <span class="text-xl">📝</span>
          <div>
            <h2 class="font-semibold text-gray-900 mb-1">설명 자동 작성</h2>
            <p class="text-sm text-gray-600">상품 설명과 마케팅 문구까지 클릭 한 번으로 완성돼요.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
  
  <!-- AI 에이전트 검색 모달 - Teleport로 body에 렌더링 -->
  <Teleport to="body">
    <div v-if="showReportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" style="z-index: 9999;">
      <div class="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
        <!-- 모달 헤더 -->
        <div class="bg-gradient-to-r from-purple-500 to-blue-500 p-6 text-white">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-lg font-bold flex items-center gap-2">
              🤖 AI 에이전트
            </h3>
            <button @click="closeReportModal" class="text-white/80 hover:text-white">✕</button>
          </div>
          <p class="text-sm text-white/90">시장 동향, 상품 분석, 전략 등 무엇이든 물어보세요!</p>
        </div>
        
        <!-- 검색 영역 -->
        <div class="p-6">
          <!-- 빠른 질문 버튼들 -->
          <div class="mb-4">
            <p class="text-sm font-medium text-gray-700 mb-3">빠른 질문 예시:</p>
            <div class="flex flex-wrap gap-2">
              <button 
                v-for="quickQuestion in quickQuestions"
                :key="quickQuestion"
                @click="searchQuery = quickQuestion"
                class="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition"
              >
                {{ quickQuestion }}
              </button>
            </div>
          </div>
          
          <!-- 검색 입력 -->
          <form @submit.prevent="handleReportSearch" class="space-y-4">
            <div>
              <textarea
                v-model="searchQuery"
                placeholder="예: 이번 달 가장 인기 있는 패션 카테고리는 무엇인가요?"
                rows="3"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition resize-none"
              ></textarea>
            </div>
            
            <button
              type="submit"
              :disabled="!searchQuery.trim() || isSearching"
              class="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium rounded-lg hover:from-purple-600 hover:to-blue-600 transition disabled:opacity-50"
            >
              {{ isSearching ? '분석 중...' : '🔍 AI에게 물어보기' }}
            </button>
          </form>
          
          <!-- 검색 결과 -->
          <div v-if="searchResult" class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              🤖 AI 답변
            </h4>
            <div class="prose prose-sm max-w-none">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ searchResult }}</p>
            </div>
            
            <!-- 추가 액션 -->
            <div class="mt-4 pt-4 border-t border-gray-200">
              <div class="flex gap-2">
                <button 
                  @click="saveReport"
                  class="flex-1 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition"
                >
                  💾 저장
                </button>
                <button 
                  @click="shareReport"
                  class="flex-1 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition"
                >
                  🔗 공유
                </button>
                <button 
                  @click="searchResult = ''; searchQuery = ''"
                  class="flex-1 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition"
                >
                  🔄 새로
                </button>
              </div>
            </div>
          </div>
          
          <!-- 로딩 상태 -->
          <div v-if="isSearching" class="mt-6 text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p class="text-gray-600 text-sm">AI가 데이터를 분석하고 있습니다...</p>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  
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
AI 리포트 기능은 로그인 후<br />
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

// Store 및 Router 초기화
const userStore = useUserStore()
const router = useRouter()

// 모달 상태
const showReportModal = ref(false)
const showLoginModal = ref(false)
const searchQuery = ref('')
const searchResult = ref('')
const isSearching = ref(false)

// 빠른 질문 예시
const quickQuestions = [
  '이번 달 인기 카테고리는?',
  '내 상품 성과 분석',
  '경쟁자 가격 비교',
  '트렌드 키워드 추천'
]

// 로그아웃 처리
const handleLogout = async () => {
  try {
    await userStore.logoutUser()
    // 로그아웃 성공 시 홈에 남아있거나 로그인 페이지로 이동
    // 여기서는 홈에 남아있는 것으로 처리
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

// 리포트 페이지로 이동
const goToReports = (type = null) => {
  // 로그인 확인
  if (!userStore.isAuthenticated) {
    showLoginModal.value = true
    return
  }
  
  // TODO: 리포트 페이지가 만들어지면 실제 라우팅
  if (type) {
    // 특정 리포트 타입으로 이동
    console.log(`${type} 리포트로 이동`)
    // router.push(`/reports/${type}`)
  } else {
    // 전체 리포트 페이지로 이동
    console.log('전체 리포트로 이동')
    // router.push('/reports')
  }
  
  // 임시로 알림 표시
  alert(`${type ? type + ' ' : ''}리포트 기능이 준비 중입니다! 🚀`)
}

// 모달 닫기
const closeReportModal = () => {
  showReportModal.value = false
  searchQuery.value = ''
  searchResult.value = ''
  isSearching.value = false
}

// 로그인 모달 닫기
const closeLoginModal = () => {
  showLoginModal.value = false
}

// AI 검색 처리
const handleReportSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  isSearching.value = true
  searchResult.value = ''
  
  try {
    // TODO: 실제 AI 에이전트 API 호출
    await new Promise(resolve => setTimeout(resolve, 2000)) // 임시 로딩
    
    // 임시 결과
    searchResult.value = `질문: "${searchQuery.value}"

📊 분석 결과:
• 현재 가장 인기 있는 카테고리는 '패션'입니다
• 지난달 대비 25% 성장했습니다
• 추천 키워드: '미니멀', '비건', '지속가능'

💡 전략 제안:
1. 여름 시즌에 맞는 가벼운 소재 활용
2. 에코 프렌들리 소재 강조
3. 가격대: 5-15만원이 가장 인기`
    
  } catch (error) {
    searchResult.value = '죄송합니다. 검색 중 오류가 발생했습니다. 다시 시도해주세요.'
  } finally {
    isSearching.value = false
  }
}

// 리포트 저장
const saveReport = () => {
  // TODO: 실제 저장 로직
  alert('리포트가 저장되었습니다! 💾')
}

// 리포트 공유
const shareReport = () => {
  // TODO: 실제 공유 로직
  if (navigator.share) {
    navigator.share({
      title: 'AI 리포트 결과',
      text: searchResult.value,
      url: window.location.href
    })
  } else {
    // 폴백: 클립보드에 복사
    navigator.clipboard.writeText(searchResult.value)
    alert('리포트가 클립보드에 복사되었습니다! 📋')
  }
}

// 추천 상품 페이지로 이동
const goToRecommendedProducts = () => {
  router.push('/recommended-products')
}

// 추천 상품 데이터 (실제로는 API에서 가져올 데이터)
const recommendedProducts = ref([
  {
    id: 1,
    name: '미니멀 화이트 스니커즈',
    user: '김소영',
    price: '89,000원',
    emoji: '👟'
  },
  {
    id: 2,
    name: '베이직 롱트 코트',
    user: '박지훈',
    price: '156,000원',
    emoji: '🧥'
  },
  {
    id: 3,
    name: '오가닉 코튼 티셔츠',
    user: '이민준',
    price: '32,000원',
    emoji: '👕'
  },
  {
    id: 4,
    name: '레더 크로스백',
    user: '정수연',
    price: '89,000원',
    emoji: '🎒'
  },
  {
    id: 5,
    name: '블루투스 이어폰',
    user: '최대호',
    price: '128,000원',
    emoji: '🎧'
  },
  {
    id: 6,
    name: '스마트워치 블랙',
    user: '송은지',
    price: '245,000원',
    emoji: '⌚'
  }
])
</script>

<style scoped>
/* 스크롤바 숨기기 */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* 텍스트 줄임 (두 줄로 제한) */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>