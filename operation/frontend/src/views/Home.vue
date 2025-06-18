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
          v-if="!loadingRecommended && recommendedProducts.length > 0 && recommendedProducts[0].id > 0"
          @click="goToRecommendedProducts"
          class="text-sm text-blue-600 hover:text-blue-700"
        >
          더보기
        </button>
      </div>
      
      <!-- 슬라이드 컨테이너 -->
      <div class="overflow-x-auto scrollbar-hide">
        <!-- 로딩 상태 -->
        <div v-if="loadingRecommended" class="flex gap-3 pb-2" style="width: max-content;">
          <div 
            v-for="n in 6" 
            :key="n"
            class="bg-white rounded-xl border border-gray-200 shadow-sm flex-shrink-0 w-40 animate-pulse"
          >
            <div class="w-full h-32 bg-gray-200 rounded-t-xl"></div>
            <div class="p-3">
              <div class="h-4 bg-gray-200 rounded mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
              <div class="h-4 bg-gray-200 rounded w-1/3"></div>
            </div>
          </div>
        </div>
        
        <!-- 빈 상태 (데이터가 없거나 에러) -->
        <div v-else-if="recommendedProducts.length === 0 || recommendedProducts[0].id <= 0" class="text-center py-8">
          <div class="text-4xl mb-3">📦</div>
          <h3 class="text-md font-semibold text-gray-900 mb-2">아직 등록된 상품이 없습니다</h3>
          <p class="text-sm text-gray-600">다른 회원들이 AI로 생성한 상품들이 곧 표시될 예정입니다</p>
        </div>
        
        <!-- 상품 목록 -->
        <div v-else class="flex gap-3 pb-2" style="width: max-content;">
          <div 
            v-for="product in recommendedProducts" 
            :key="product.id"
            class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex-shrink-0 w-40"
          >
            <!-- 상품 이미지 -->
            <div class="relative">
              <div class="w-full h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-xl flex items-center justify-center overflow-hidden">
                <img 
                  v-if="product.imageUrl" 
                  :src="product.imageUrl" 
                  :alt="product.username"
                  class="w-full h-full object-cover"
                  @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
                />
                <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100">
                  <span class="text-3xl">{{ product.emoji }}</span>
                </div>
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
              <span class="text-xl text-white">🤖</span>
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">AI 리포트</h2>
              <p class="text-sm text-gray-600">무엇이든 AI에게 물어보세요</p>
            </div>
          </div>
        </div>
        
        <!-- 빠른 질문 예시 카드들 -->
        <div class="grid grid-cols-2 gap-3 mb-4">
          <div class="bg-white/70 rounded-xl p-4 text-left">
            <div class="text-lg mb-2">📈</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">트렌드 분석</h3>
            <p class="text-xs text-gray-600">시장 동향과 인기 상품</p>
          </div>
          
          <div class="bg-white/70 rounded-xl p-4 text-left">
            <div class="text-lg mb-2">💰</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">비즈니스 전략</h3>
            <p class="text-xs text-gray-600">창업과 운영 노하우</p>
          </div>
          
          <div class="bg-white/70 rounded-xl p-4 text-left">
            <div class="text-lg mb-2">🎯</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">마케팅 인사이트</h3>
            <p class="text-xs text-gray-600">효과적인 홍보 방법</p>
          </div>
          
          <div class="bg-white/70 rounded-xl p-4 text-left">
            <div class="text-lg mb-2">🌐</div>
            <h3 class="font-semibold text-gray-900 text-sm mb-1">경쟁사 분석</h3>
            <p class="text-xs text-gray-600">업계 동향 파악</p>
          </div>
        </div>
        
        <!-- AI 에이전트 검색 버튼 -->
        <button 
          @click="goToReportPage"
          class="w-full py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium rounded-xl hover:from-purple-600 hover:to-blue-600 transition-all"
        >
          🔍 AI에게 물어보기
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
import { ref, Teleport, onMounted } from 'vue'
import { useUserStore } from '@/store/userStore'
import { useRouter } from 'vue-router'
import { getRecommendedProducts } from '@/api/products.js'

// Store 및 Router 초기화
const userStore = useUserStore()
const router = useRouter()

// 모달 상태
const showLoginModal = ref(false)

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
const goToReportPage = () => {
  // 로그인 확인
  if (!userStore.isAuthenticated) {
    showLoginModal.value = true
    return
  }
  
  // 리포트 페이지로 이동
  router.push('/report')
}

// 로그인 모달 닫기
const closeLoginModal = () => {
  showLoginModal.value = false
}

// 추천 상품 페이지로 이동
const goToRecommendedProducts = () => {
  router.push('/recommended-products')
}

// 추천 상품 데이터
const recommendedProducts = ref([])
const loadingRecommended = ref(false)

// 추천 상품 로드 함수
const loadRecommendedProducts = async () => {
  try {
    loadingRecommended.value = true
    const response = await getRecommendedProducts(6) // 홈 화면에서는 6개만 표시
    
    // API 응답 데이터를 UI 형식에 맞게 변환
    const transformedProducts = response.map(product => ({
      id: product.id,
      name: product.product_name,
      user: product.username,
      price: product.price ? `${product.price.toLocaleString()}원` : '가격미정',
      emoji: getCategoryEmoji(product.category),
      imageUrl: product.image_url
    }))
    
    recommendedProducts.value = transformedProducts
    
  } catch (error) {
    console.error('추천 상품 로드 실패:', error)
    // 에러 시 빈 배열 반환 (중앙 메시지로 처리)
    recommendedProducts.value = []
  } finally {
    loadingRecommended.value = false
  }
}

// 카테고리별 이모지 매핑
const getCategoryEmoji = (category) => {
  const emojiMap = {
    '패션': '👕',
    '전자제품': '📱',
    '홈/리빙': '🏠',
    '뷰티': '💄',
    '스포츠': '⚽',
    '도서': '📚',
    '식품': '🍎',
    '기타': '📦'
  }
  return emojiMap[category] || '📦'
}

// 컴포넌트 마운트 시 추천 상품 로드
onMounted(() => {
  loadRecommendedProducts()
})
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