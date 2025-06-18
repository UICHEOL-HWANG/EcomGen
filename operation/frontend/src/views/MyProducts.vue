<template>
  <div class="px-4 py-6 pb-20">
    <!-- 에러 메시지 표시 -->
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl">
      <p class="text-sm text-red-600">{{ errorMessage }}</p>
      <button 
        @click="loadMyProducts"
        class="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
      >
        다시 시도
      </button>
    </div>

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
            <h1 class="text-xl font-bold text-gray-900">📦 내가 만든 상품</h1>
            <p class="text-sm text-gray-600">AI로 생성한 나만의 상품들</p>
          </div>
        </div>
        
        <!-- 정렬 버튼 -->
        <button 
          @click="showSortModal = true"
          class="w-10 h-10 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-50 transition"
        >
          <span class="text-lg">⏏️</span>
        </button>
      </div>
    </section>

    <!-- 통계 카드 -->
    <section class="mb-6">
      <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ myProducts.length }}</div>
              <div class="text-xs text-gray-600">총 상품</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ Math.max(0, categories.length - 1) }}</div>
              <div class="text-xs text-gray-600">카테고리</div>
            </div>
          </div>
          <div class="text-4xl">🚀</div>
        </div>
      </div>
    </section>

    <!-- 카테고리 필터 -->
    <section class="mb-6">
      <div class="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
        <button 
          v-for="category in categories"
          :key="category"
          @click="onCategoryChange(category)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition flex-shrink-0',
            selectedCategory === category 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ category }}
        </button>
      </div>
    </section>

    <!-- 상품 목록 -->
    <section>
      <!-- 로딩 상태 -->
      <div v-if="loading" class="space-y-4">
        <div v-for="n in 3" :key="n" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
          <div class="flex gap-4">
            <div class="w-20 h-20 bg-gray-200 rounded-lg"></div>
            <div class="flex-1 space-y-2">
              <div class="h-4 bg-gray-200 rounded w-3/4"></div>
              <div class="h-3 bg-gray-200 rounded w-1/2"></div>
              <div class="h-3 bg-gray-200 rounded w-1/4"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 상품 목록 -->
      <div v-else-if="myProducts.length > 0" class="space-y-4">
        <div 
          v-for="product in myProducts" 
          :key="product.id"
          @click="openProductDetail(product)"
          class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        >
          <div class="p-4">
            <div class="flex gap-4">
              <!-- 상품 이미지 -->
              <div class="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <img 
                  v-if="product.imageUrl" 
                  :src="product.imageUrl" 
                  :alt="product.name"
                  class="w-full h-full object-cover rounded-lg"
                />
                <span v-else class="text-3xl">{{ product.emoji }}</span>
              </div>
              
              <!-- 상품 정보 -->
              <div class="flex-1 min-w-0">
                <h3 class="font-bold text-gray-900 line-clamp-1 mb-2">{{ product.name }}</h3>
                
                <p class="text-sm text-gray-600 mb-2 line-clamp-2">{{ product.description }}</p>
                
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      {{ product.category }}
                    </span>
                    <span class="text-xs text-gray-500">{{ product.createdAt }}</span>
                  </div>
                  <span class="text-sm font-bold text-blue-600">{{ product.price }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">📦</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          {{ selectedCategory === '전체' ? '아직 생성한 상품이 없습니다' : '해당 카테고리에 상품이 없습니다' }}
        </h3>
        <p class="text-gray-600 mb-4">
          {{ selectedCategory === '전체' ? 'AI로 첫 번째 상품을 만들어보세요!' : '다른 카테고리를 선택해보세요.' }}
        </p>
        <router-link 
          v-if="selectedCategory === '전체'"
          to="/generate"
          class="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
        >
          상품 생성하러 가기
        </router-link>
      </div>
    </section>

    <!-- 정렬 모달 -->
    <div v-if="showSortModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-sm w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">정렬 기준</h3>
          <button @click="showSortModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        
        <div class="space-y-3">
          <label v-for="sort in sortOptions" :key="sort.value" class="flex items-center">
            <input 
              v-model="selectedSort" 
              :value="sort.value" 
              type="radio" 
              name="sort"
              class="mr-3 text-blue-600"
            />
            <span class="text-gray-700">{{ sort.label }}</span>
          </label>
        </div>

        <div class="mt-6 flex gap-3">
          <button 
            @click="showSortModal = false"
            class="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
          >
            취소
          </button>
          <button 
            @click="applySort"
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
            <img 
              v-if="selectedProduct.imageUrl" 
              :src="selectedProduct.imageUrl" 
              :alt="selectedProduct.name"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-8xl">{{ selectedProduct.emoji }}</span>
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
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-xl font-bold text-gray-900">{{ selectedProduct.name }}</h2>
            <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
              {{ selectedProduct.category }}
            </span>
          </div>
          
          <div class="flex items-center gap-2 mb-4">
            <span class="text-gray-500 text-sm">{{ selectedProduct.createdAt }} 생성</span>
          </div>
          
          <div class="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 class="font-semibold text-gray-900 mb-2">상품 설명</h3>
            <p class="text-gray-700 leading-relaxed">{{ selectedProduct.description }}</p>
          </div>
          
          <div class="flex items-center justify-between mb-6">
            <span class="text-gray-600">예상 가격</span>
            <span class="text-2xl font-bold text-blue-600">{{ selectedProduct.price }}</span>
          </div>
          
          <div class="space-y-3">
            <button 
              @click="editProduct(selectedProduct)"
              class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
            >
              상품 수정하기
            </button>
            <button 
              @click="shareProduct(selectedProduct)"
              class="w-full py-3 border border-blue-600 text-blue-600 font-medium rounded-lg hover:bg-blue-50 transition"
            >
              상품 공유하기
            </button>
            <button 
              @click="deleteProduct(selectedProduct)"
              class="w-full py-2 text-red-600 font-medium hover:bg-red-50 rounded-lg transition"
            >
              상품 삭제하기
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { getMyProducts, deleteMyProduct } from '@/api/products'

const router = useRouter()
const userStore = useUserStore()

// 상태 관리
const loading = ref(true)
const selectedCategory = ref('전체')
const selectedSort = ref('latest')
const showSortModal = ref(false)
const selectedProduct = ref(null)
const errorMessage = ref('')

// 실제 데이터
const myProducts = ref([])
const availableCategories = ref(['전체'])

// 정렬 옵션
const sortOptions = ref([
  { value: 'latest', label: '최신순' },
  { value: 'oldest', label: '오래된순' },
  { value: 'name', label: '이름순' },
  { value: 'price_low', label: '가격 낮은순' },
  { value: 'price_high', label: '가격 높은순' }
])

// 유틸리티 함수들
const getEmojiForCategory = (category) => {
  const emojiMap = {
    '패션': '👕',
    '의류': '👔',
    '신발': '👟',
    '전자제품': '📱',
    '가전제품': '📺',
    '홈/리빙': '🏠',
    '가구': '🪑',
    '뷰티': '💄',
    '화장품': '💅',
    '음식': '🍔',
    '식품': '🥘',
    '스포츠': '⚽',
    '운동': '🏃',
    '도서': '📚',
    '문구': '✏️',
    '자동차': '🚗',
    '반려동물': '🐕',
    '육아': '👶',
    '기타': '📦'
  }
  return emojiMap[category] || '📦'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 실제 데이터 로드 함수
const loadMyProducts = async () => {
  try {
    loading.value = true
    errorMessage.value = ''
    
    const response = await getMyProducts({
      category: selectedCategory.value === '전체' ? null : selectedCategory.value,
      sort_by: selectedSort.value,
      limit: 50,
      offset: 0
    })
    
    // 데이터 변환
    myProducts.value = response.products.map(product => ({
      id: product.id,
      name: product.product_name,
      description: product.description,
      price: product.price ? `${product.price.toLocaleString()}원` : '가격 미정',
      emoji: getEmojiForCategory(product.category),
      category: product.category || '기타',
      createdAt: formatDate(product.created_at),
      imageUrl: product.image_url,
      isFavorite: false, // 즐겨찾기 기능 제거됨
      keywords: product.keywords || [],
      tone: product.tone,
      jobId: product.job_id
    }))
    
    // 카테고리 목록 업데이트 
    availableCategories.value = ['전체', ...response.categories]
    
  } catch (error) {
    console.error('상품 로드 실패:', error)
    errorMessage.value = error.message
    myProducts.value = []
  } finally {
    loading.value = false
  }
}

// 계산된 속성들
const categories = computed(() => availableCategories.value)

// 이벤트 핸들러들
const onCategoryChange = async (category) => {
  selectedCategory.value = category
  await loadMyProducts()
}

const applySort = async () => {
  showSortModal.value = false
  await loadMyProducts()
}

const goBack = () => {
  router.go(-1)
}

const openProductDetail = (product) => {
  selectedProduct.value = product
}

const toggleFavorite = (product) => {
  // 즐겨찾기 기능이 제거되었습니다
}

const editProduct = (product) => {
  // TODO: 상품 수정 페이지로 이동
  router.push(`/generate?edit=${product.id}`)
}

const shareProduct = (product) => {
  if (navigator.share) {
    navigator.share({
      title: product.name,
      text: product.description,
      url: `${window.location.origin}/product/${product.id}`
    })
  } else {
    // 폴백: 클립보드에 복사
    const shareText = `${product.name}\n${product.description}\n${window.location.origin}/product/${product.id}`
    navigator.clipboard.writeText(shareText)
    alert('상품 정보가 클립보드에 복사되었습니다! 📋')
  }
}

const deleteProduct = async (product) => {
  if (confirm(`"${product.name}" 상품을 삭제하시겠습니까?`)) {
    try {
      await deleteMyProduct(product.id)
      selectedProduct.value = null
      await loadMyProducts() // 목록 새로고침
      alert('상품이 성공적으로 삭제되었습니다.')
    } catch (error) {
      console.error('상품 삭제 실패:', error)
      alert('상품 삭제에 실패했습니다.')
    }
  }
}

// 컴포넌트 마운트 시
onMounted(async () => {
  await loadMyProducts()
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
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>