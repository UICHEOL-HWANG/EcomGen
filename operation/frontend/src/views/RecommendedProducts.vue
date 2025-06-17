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
          @click="onCategoryChange(category.id)"
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
        <div v-for="n in 3" :key="n" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
          <div class="w-full h-48 bg-gray-200 rounded-lg mb-4"></div>
          <div class="h-4 bg-gray-200 rounded mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>

      <!-- 상품 목록 -->
      <div v-else class="space-y-4">
        <div 
          v-for="product in displayedProducts" 
          :key="product.id"
          @click="openProductDetail(product)"
          class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        >
          <!-- 상품 이미지 -->
          <div class="relative">
            <div class="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-xl flex items-center justify-center overflow-hidden">
              <img 
                v-if="product.imageUrl" 
                :src="product.imageUrl" 
                :alt="product.name"
                class="w-full h-full object-cover"
                @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
              />
              <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100">
                <span class="text-6xl">{{ product.emoji }}</span>
              </div>
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
                <!-- 프로필 사진 또는 이모지 -->
                <div class="w-6 h-6 rounded-full flex items-center justify-center overflow-hidden">
                  <img 
                    v-if="product.profile_pic" 
                    :src="product.profile_pic" 
                    :alt="product.user"
                    class="w-full h-full object-cover"
                    @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
                  />
                  <div v-else class="w-full h-full bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-xs">👤</span>
                  </div>
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

      <!-- 더 보기 버튼 -->
      <div v-if="canShowMore && !loading" class="mt-6 text-center">
        <button 
          @click="showMore"
          class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
        >
          더 보기 ({{ remainingCount }}개 더 있음)
        </button>
      </div>

      <!-- 에러 상태 -->
      <div v-if="error && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">⚠️</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">오류가 발생했습니다</h3>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button 
          @click="loadProducts()"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          다시 시도
        </button>
      </div>

      <!-- 빈 상태 -->
      <div v-else-if="!loading && !error && filteredProducts.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">📦</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">아직 등록된 상품이 없습니다</h3>
        <p class="text-gray-600 mb-4">다른 회원들이 AI로 생성한 상품들이<br />곧 여기에 표시될 예정입니다</p>
        <button 
          @click="loadProducts()"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          새로고침
        </button>
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
          <div class="w-full h-64 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center overflow-hidden">
            <img 
              v-if="selectedProduct.imageUrl" 
              :src="selectedProduct.imageUrl" 
              :alt="selectedProduct.name"
              class="w-full h-full object-cover"
              @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100">
              <span class="text-8xl">{{ selectedProduct.emoji }}</span>
            </div>
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
            <!-- 프로필 사진 또는 이모지 -->
            <div class="w-8 h-8 rounded-full flex items-center justify-center overflow-hidden">
              <img 
                v-if="selectedProduct.profile_pic" 
                :src="selectedProduct.profile_pic" 
                :alt="selectedProduct.user"
                class="w-full h-full object-cover"
                @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'"
              />
              <div v-else class="w-full h-full bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-sm">👤</span>
              </div>
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
import { getRecommendedProducts, getRecommendedProductCategories } from '@/api/products.js'

const router = useRouter()

// 상태 관리
const loading = ref(true)
const selectedCategory = ref('all')
const selectedSort = ref('latest')
const selectedPriceRange = ref('all')
const showFilterModal = ref(false)
const selectedProduct = ref(null)
const showAllProducts = ref(false)

// 카테고리 목록 (동적으로 생성)
const categories = ref([{ id: 'all', name: '전체' }])

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

// 상품 데이터
const products = ref([])
const error = ref(null)

// 카테고리 선택 시 상품 다시 로드
const onCategoryChange = async (categoryId) => {
  selectedCategory.value = categoryId
  showAllProducts.value = false // 카테고리 변경 시 다시 3개로 제한
  await loadProducts()
}

// 카테고리 목록 로드
const loadCategories = async () => {
  try {
    const categoryList = await getRecommendedProductCategories()
    const dynamicCategories = categoryList.map(category => ({
      id: category,
      name: category
    }))
    
    categories.value = [
      { id: 'all', name: '전체' },
      ...dynamicCategories
    ]
  } catch (err) {
    console.error('카테고리 로드 실패:', err)
    // 카테고리 로드 실패 시 기본 카테고리만 사용
    categories.value = [{ id: 'all', name: '전체' }]
  }
}

// 실제 데이터 로드 함수
const loadProducts = async (limit = 50) => {
  try {
    loading.value = true
    error.value = null
    
    // 선택된 카테고리에 따라 API 호출
    const categoryParam = selectedCategory.value === 'all' ? null : selectedCategory.value
    const response = await getRecommendedProducts(limit, categoryParam)
    
    // API 응답 데이터를 UI 형식에 맞게 변환
    const transformedProducts = response.map(product => ({
      id: product.id,
      name: product.product_name,
      description: product.description,
      price: product.price ? `${product.price.toLocaleString()}원` : '가격미정',
      category: product.category,
      emoji: getCategoryEmoji(product.category),
      user: product.username,
      profile_pic: product.profile_pic,
      createdAt: formatDate(product.created_at),
      imageUrl: product.image_url,
      keywords: product.keywords,
      tone: product.tone
    }))
    
    products.value = transformedProducts
    
  } catch (err) {
    console.error('추천 상품 로드 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
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

// 날짜 포맷팅
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now - date) / (1000 * 60 * 60))
  
  if (diffInHours < 1) return '방금 전'
  if (diffInHours < 24) return `${diffInHours}시간 전`
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}일 전`
  return date.toLocaleDateString()
}



// 필터된 상품 목록 (이제 백엔드에서 필터링하므로 단순화)
const filteredProducts = computed(() => {
  let filtered = products.value

  // 정렬 (로컬 정렬)
  if (selectedSort.value === 'latest') {
    // 최신순 (이미 기본 정렬)
  } else if (selectedSort.value === 'popular') {
    // 인기순 (임시로 이름 순으로)
    filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name))
  } else if (selectedSort.value === 'price_low') {
    // 가격 낮은순
    filtered = [...filtered].sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, '')) || 0
      const priceB = parseInt(b.price.replace(/[^0-9]/g, '')) || 0
      return priceA - priceB
    })
  } else if (selectedSort.value === 'price_high') {
    // 가격 높은순
    filtered = [...filtered].sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, '')) || 0
      const priceB = parseInt(b.price.replace(/[^0-9]/g, '')) || 0
      return priceB - priceA
    })
  }

  // 가격 범위 필터 (로컬 필터링)
  if (selectedPriceRange.value !== 'all') {
    if (selectedPriceRange.value === '0-50000') {
      filtered = filtered.filter(product => {
        const price = parseInt(product.price.replace(/[^0-9]/g, '')) || 0
        return price <= 50000
      })
    } else if (selectedPriceRange.value === '50000-100000') {
      filtered = filtered.filter(product => {
        const price = parseInt(product.price.replace(/[^0-9]/g, '')) || 0
        return price > 50000 && price <= 100000
      })
    } else if (selectedPriceRange.value === '100000-200000') {
      filtered = filtered.filter(product => {
        const price = parseInt(product.price.replace(/[^0-9]/g, '')) || 0
        return price > 100000 && price <= 200000
      })
    } else if (selectedPriceRange.value === '200000+') {
      filtered = filtered.filter(product => {
        const price = parseInt(product.price.replace(/[^0-9]/g, '')) || 0
        return price > 200000
      })
    }
  }

  return filtered
})

// 표시할 상품 목록 (최대 3개 또는 전체)
const displayedProducts = computed(() => {
  if (showAllProducts.value) {
    return filteredProducts.value
  }
  return filteredProducts.value.slice(0, 3)
})

// 더 보기 버튼 표시 여부
const canShowMore = computed(() => {
  return !showAllProducts.value && filteredProducts.value.length > 3
})

// 남은 상품 개수
const remainingCount = computed(() => {
  return Math.max(0, filteredProducts.value.length - 3)
})

// 뒤로 가기
const goBack = () => {
  router.go(-1)
}

// 더 보기
const showMore = () => {
  showAllProducts.value = true
}

// 상품 상세 보기
const openProductDetail = (product) => {
  selectedProduct.value = product
}

// 필터 적용
const applyFilters = async () => {
  showFilterModal.value = false
  showAllProducts.value = false // 필터 적용 시 다시 3개로 제한
  await loadProducts() // 데이터 다시 로드
}

// 필터 초기화
const resetFilters = async () => {
  selectedCategory.value = 'all'
  selectedSort.value = 'latest'
  selectedPriceRange.value = 'all'
  showAllProducts.value = false
  await loadProducts() // 데이터 다시 로드
}

// 컴포넌트 마운트 시
onMounted(async () => {
  await loadCategories() // 카테고리 먼저 로드
  await loadProducts()   // 그 다음 상품 로드
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