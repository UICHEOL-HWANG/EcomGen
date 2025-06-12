<template>
  <div class="px-4 py-6 pb-20">
    <!-- 헤더 -->
    <section class="mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button 
            @click="goBack"
            class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition"
          >
            <span class="text-xl">←</span>
          </button>
          <div>
            <h1 class="text-xl font-bold text-gray-900">🔥 추천 상품</h1>
            <p class="text-sm text-gray-600">다른 회원들이 AI로 생성한 상품들</p>
          </div>
        </div>
        
        <!-- 필터 버튼 -->
        <button 
          @click="showFilterModal = true"
          class="w-10 h-10 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-50 transition"
        >
          <span class="text-lg">🔍</span>
        </button>
      </div>
    </section>

    <!-- 카테고리 필터 -->
    <section class="mb-6">
      <div class="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
        <button 
          v-for="category in categories"
          :key="category.id"
          @click="selectedCategory = category.id"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition flex-shrink-0',
            selectedCategory === category.id 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ category.name }}
        </button>
      </div>
    </section>

    <!-- 상품 그리드 -->
    <section>
      <!-- 로딩 상태 -->
      <div v-if="loading" class="space-y-4">
        <div v-for="n in 6" :key="n" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
          <div class="w-full h-48 bg-gray-200 rounded-lg mb-4"></div>
          <div class="h-4 bg-gray-200 rounded mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>

      <!-- 상품 목록 -->
      <div v-else class="space-y-4">
        <div 
          v-for="product in filteredProducts" 
          :key="product.id"
          @click="openProductDetail(product)"
          class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        >
          <!-- 상품 이미지 -->
          <div class="relative">
            <div class="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-xl flex items-center justify-center">
              <span class="text-6xl">{{ product.emoji }}</span>
            </div>
            <div class="absolute top-3 right-3 bg-white rounded-full px-3 py-1 text-xs text-gray-600 shadow-sm">
              AI 생성
            </div>
            <div class="absolute top-3 left-3 bg-black bg-opacity-50 rounded-full px-2 py-1 text-xs text-white">
              {{ product.category }}
            </div>
          </div>
          
          <!-- 상품 정보 -->
          <div class="p-4">
            <h3 class="font-bold text-lg text-gray-900 mb-2 line-clamp-2">{{ product.name }}</h3>
            <p class="text-sm text-gray-600 mb-3 line-clamp-3">{{ product.description }}</p>
            
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                  <span class="text-xs">👤</span>
                </div>
                <span class="text-sm text-gray-600">{{ product.user }}님</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-500">{{ product.createdAt }}</span>
                <span class="text-lg font-bold text-blue-600">{{ product.price }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 더 로드하기 버튼 -->
      <div v-if="hasMore && !loading" class="mt-8 text-center">
        <button 
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loadingMore ? '로딩 중...' : '더 보기' }}
        </button>
      </div>

      <!-- 빈 상태 -->
      <div v-if="!loading && filteredProducts.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">🔍</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">상품이 없습니다</h3>
        <p class="text-gray-600">다른 카테고리를 선택해보세요</p>
      </div>
    </section>

    <!-- 필터 모달 -->
    <div v-if="showFilterModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-sm w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">필터 설정</h3>
          <button @click="showFilterModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        
        <!-- 정렬 옵션 -->
        <div class="mb-6">
          <h4 class="font-semibold text-gray-900 mb-3">정렬</h4>
          <div class="space-y-2">
            <label v-for="sort in sortOptions" :key="sort.value" class="flex items-center">
              <input 
                v-model="selectedSort" 
                :value="sort.value" 
                type="radio" 
                class="mr-3 text-blue-600"
              />
              <span class="text-gray-700">{{ sort.label }}</span>
            </label>
          </div>
        </div>

        <!-- 가격 범위 -->
        <div class="mb-6">
          <h4 class="font-semibold text-gray-900 mb-3">가격 범위</h4>
          <div class="space-y-2">
            <label v-for="price in priceRanges" :key="price.value" class="flex items-center">
              <input 
                v-model="selectedPriceRange" 
                :value="price.value" 
                type="radio" 
                class="mr-3 text-blue-600"
              />
              <span class="text-gray-700">{{ price.label }}</span>
            </label>
          </div>
        </div>

        <!-- 버튼들 -->
        <div class="flex gap-3">
          <button 
            @click="resetFilters"
            class="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
          >
            초기화
          </button>
          <button 
            @click="applyFilters"
            class="flex-1 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            적용
          </button>
        </div>
      </div>
    </div>

    <!-- 상품 상세 모달 -->
    <div v-if="selectedProduct" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-y-auto">
        <!-- 상품 이미지 -->
        <div class="relative">
          <div class="w-full h-64 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
            <span class="text-8xl">{{ selectedProduct.emoji }}</span>
          </div>
          <button 
            @click="selectedProduct = null"
            class="absolute top-4 right-4 w-10 h-10 bg-black bg-opacity-50 rounded-full flex items-center justify-center text-white hover:bg-opacity-70 transition"
          >
            ✕
          </button>
        </div>
        
        <!-- 상품 정보 -->
        <div class="p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-2">{{ selectedProduct.name }}</h2>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-sm">👤</span>
            </div>
            <span class="text-gray-600">{{ selectedProduct.user }}님이 생성</span>
            <span class="text-gray-400">•</span>
            <span class="text-gray-500 text-sm">{{ selectedProduct.createdAt }}</span>
          </div>
          
          <div class="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 class="font-semibold text-gray-900 mb-2">상품 설명</h3>
            <p class="text-gray-700 leading-relaxed">{{ selectedProduct.description }}</p>
          </div>
          
          <div class="flex items-center justify-between mb-6">
            <span class="text-gray-600">예상 가격</span>
            <span class="text-2xl font-bold text-blue-600">{{ selectedProduct.price }}</span>
          </div>
          
          <button class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
            비슷한 상품 생성하기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 상태 관리
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)
const selectedCategory = ref('all')
const selectedSort = ref('latest')
const selectedPriceRange = ref('all')
const showFilterModal = ref(false)
const selectedProduct = ref(null)

// 카테고리 목록
const categories = ref([
  { id: 'all', name: '전체' },
  { id: 'fashion', name: '패션' },
  { id: 'electronics', name: '전자제품' },
  { id: 'home', name: '홈/리빙' },
  { id: 'beauty', name: '뷰티' },
  { id: 'sports', name: '스포츠' },
  { id: 'books', name: '도서' },
  { id: 'food', name: '식품' }
])

// 정렬 옵션
const sortOptions = ref([
  { value: 'latest', label: '최신순' },
  { value: 'popular', label: '인기순' },
  { value: 'price_low', label: '가격 낮은순' },
  { value: 'price_high', label: '가격 높은순' }
])

// 가격 범위
const priceRanges = ref([
  { value: 'all', label: '전체' },
  { value: '0-50000', label: '5만원 이하' },
  { value: '50000-100000', label: '5만원 - 10만원' },
  { value: '100000-200000', label: '10만원 - 20만원' },
  { value: '200000+', label: '20만원 이상' }
])

// 상품 데이터 (실제로는 API에서 가져올 데이터)
const products = ref([
  {
    id: 1,
    name: '미니멀 화이트 스니커즈',
    description: '깔끔한 디자인의 화이트 스니커즈로 어떤 옷에도 잘 어울리는 기본 아이템입니다. 편안한 착용감과 세련된 실루엣으로 데일리 룩의 완성도를 높여줍니다.',
    user: '김소영',
    price: '89,000원',
    emoji: '👟',
    category: '패션',
    createdAt: '2시간 전'
  },
  {
    id: 2,
    name: '베이직 롱 코트',
    description: '가을과 겨울을 위한 따뜻하고 스타일리시한 롱 코트입니다. 고급스러운 울 소재로 제작되어 보온성과 패션성을 모두 만족시킵니다.',
    user: '박지훈',
    price: '156,000원',
    emoji: '🧥',
    category: '패션',
    createdAt: '4시간 전'
  },
  {
    id: 3,
    name: '오가닉 코튼 티셔츠',
    description: '100% 오가닉 코튼으로 만든 친환경 티셔츠입니다. 부드러운 촉감과 우수한 통기성으로 사계절 내내 편안하게 착용할 수 있습니다.',
    user: '이민준',
    price: '32,000원',
    emoji: '👕',
    category: '패션',
    createdAt: '6시간 전'
  },
  {
    id: 4,
    name: '레더 크로스백',
    description: '진짜 가죽으로 제작된 고급스러운 크로스백입니다. 컴팩트한 사이즈에 실용적인 수납공간으로 데일리 아이템으로 완벽합니다.',
    user: '정수연',
    price: '89,000원',
    emoji: '🎒',
    category: '패션',
    createdAt: '8시간 전'
  },
  {
    id: 5,
    name: '블루투스 이어폰',
    description: '고음질 사운드와 긴 배터리 수명을 자랑하는 무선 이어폰입니다. 액티브 노이즈 캐슬링 기능으로 몰입감 있는 음악 감상이 가능합니다.',
    user: '최대호',
    price: '128,000원',
    emoji: '🎧',
    category: '전자제품',
    createdAt: '10시간 전'
  },
  {
    id: 6,
    name: '스마트워치 블랙',
    description: '건강 관리와 스마트 기능을 한번에! 심박수, 운동량, 수면 패턴을 정확하게 측정하고 스마트폰과 연동되어 편리한 사용이 가능합니다.',
    user: '송은지',
    price: '245,000원',
    emoji: '⌚',
    category: '전자제품',
    createdAt: '12시간 전'
  },
  {
    id: 7,
    name: '아로마 디퓨저',
    description: '자연스러운 향기로 공간을 채워주는 우드 디퓨저입니다. 타이머 기능과 LED 조명으로 분위기까지 연출할 수 있습니다.',
    user: '윤서진',
    price: '45,000원',
    emoji: '🕯️',
    category: '홈/리빙',
    createdAt: '1일 전'
  },
  {
    id: 8,
    name: '비타민 C 세럼',
    description: '순수 비타민 C 20% 함유로 피부 톤업과 탄력 개선에 효과적입니다. 민감한 피부도 안심하고 사용할 수 있는 순한 성분으로 제작되었습니다.',
    user: '김태영',
    price: '38,000원',
    emoji: '🧴',
    category: '뷰티',
    createdAt: '1일 전'
  }
])

// 필터된 상품 목록
const filteredProducts = computed(() => {
  let filtered = products.value

  // 카테고리 필터
  if (selectedCategory.value !== 'all') {
    const categoryName = categories.value.find(c => c.id === selectedCategory.value)?.name
    filtered = filtered.filter(product => product.category === categoryName)
  }

  // 정렬
  if (selectedSort.value === 'latest') {
    // 최신순 (이미 기본 정렬)
  } else if (selectedSort.value === 'popular') {
    // 인기순 (임시로 이름 순으로)
    filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name))
  } else if (selectedSort.value === 'price_low') {
    // 가격 낮은순
    filtered = [...filtered].sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, ''))
      const priceB = parseInt(b.price.replace(/[^0-9]/g, ''))
      return priceA - priceB
    })
  } else if (selectedSort.value === 'price_high') {
    // 가격 높은순
    filtered = [...filtered].sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, ''))
      const priceB = parseInt(b.price.replace(/[^0-9]/g, ''))
      return priceB - priceA
    })
  }

  return filtered
})

// 뒤로 가기
const goBack = () => {
  router.go(-1)
}

// 더 로드하기
const loadMore = async () => {
  loadingMore.value = true
  // 실제로는 API 호출
  await new Promise(resolve => setTimeout(resolve, 1000))
  loadingMore.value = false
  // hasMore.value = false // 더 이상 로드할 데이터가 없을 때
}

// 상품 상세 보기
const openProductDetail = (product) => {
  selectedProduct.value = product
}

// 필터 적용
const applyFilters = () => {
  showFilterModal.value = false
  // 필터가 적용된 상태로 상품 목록 새로고침
}

// 필터 초기화
const resetFilters = () => {
  selectedCategory.value = 'all'
  selectedSort.value = 'latest'
  selectedPriceRange.value = 'all'
}

// 컴포넌트 마운트 시
onMounted(async () => {
  // 실제로는 API에서 상품 목록 로드
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
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

/* 텍스트 줄임 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
