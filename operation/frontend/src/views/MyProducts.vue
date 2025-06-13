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
            <h1 class="text-xl font-bold text-gray-900">📦 내가 만든 상품</h1>
            <p class="text-sm text-gray-600">AI로 생성한 나만의 상품들</p>
          </div>
        </div>
        
        <!-- 정렬 버튼 -->
        <button 
          @click="showSortModal = true"
          class="w-10 h-10 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-50 transition"
        >
          <span class="text-lg">↕️</span>
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
              <div class="text-2xl font-bold text-green-600">{{ favoriteProducts.length }}</div>
              <div class="text-xs text-gray-600">즐겨찾기</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ categories.length }}</div>
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
          @click="selectedCategory = category"
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
      <div v-else-if="filteredProducts.length > 0" class="space-y-4">
        <div 
          v-for="product in filteredProducts" 
          :key="product.id"
          @click="openProductDetail(product)"
          class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        >
          <div class="p-4">
            <div class="flex gap-4">
              <!-- 상품 이미지 -->
              <div class="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span class="text-3xl">{{ product.emoji }}</span>
              </div>
              
              <!-- 상품 정보 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between mb-2">
                  <h3 class="font-bold text-gray-900 line-clamp-1">{{ product.name }}</h3>
                  <button 
                    @click.stop="toggleFavorite(product)"
                    class="text-lg flex-shrink-0 ml-2"
                  >
                    {{ product.isFavorite ? '❤️' : '🤍' }}
                  </button>
                </div>
                
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
            <span class="text-8xl">{{ selectedProduct.emoji }}</span>
          </div>
          <button 
            @click="selectedProduct = null"
            class="absolute top-4 right-4 w-10 h-10 bg-black bg-opacity-50 rounded-full flex items-center justify-center text-white hover:bg-opacity-70 transition"
          >
            ✕
          </button>
          <button 
            @click="toggleFavorite(selectedProduct)"
            class="absolute top-4 left-4 w-10 h-10 bg-black bg-opacity-50 rounded-full flex items-center justify-center hover:bg-opacity-70 transition"
          >
            {{ selectedProduct.isFavorite ? '❤️' : '🤍' }}
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

const router = useRouter()
const userStore = useUserStore()

// 상태 관리
const loading = ref(true)
const selectedCategory = ref('전체')
const selectedSort = ref('latest')
const showSortModal = ref(false)
const selectedProduct = ref(null)

// 정렬 옵션
const sortOptions = ref([
  { value: 'latest', label: '최신순' },
  { value: 'oldest', label: '오래된순' },
  { value: 'name', label: '이름순' },
  { value: 'price_low', label: '가격 낮은순' },
  { value: 'price_high', label: '가격 높은순' },
  { value: 'favorite', label: '즐겨찾기 우선' }
])

// 내가 만든 상품 데이터 (실제로는 API에서 가져올 데이터)
const myProducts = ref([
  {
    id: 1,
    name: '미니멀 화이트 스니커즈',
    description: '깔끔한 디자인의 화이트 스니커즈로 어떤 옷에도 잘 어울리는 기본 아이템입니다. 편안한 착용감과 세련된 실루엣으로 데일리 룩의 완성도를 높여줍니다.',
    price: '89,000원',
    emoji: '👟',
    category: '패션',
    createdAt: '2024-01-15',
    isFavorite: true
  },
  {
    id: 2,
    name: '베이직 롱 코트',
    description: '가을과 겨울을 위한 따뜻하고 스타일리시한 롱 코트입니다. 고급스러운 울 소재로 제작되어 보온성과 패션성을 모두 만족시킵니다.',
    price: '156,000원',
    emoji: '🧥',
    category: '패션',
    createdAt: '2024-01-10',
    isFavorite: false
  },
  {
    id: 3,
    name: '블루투스 이어폰',
    description: '고음질 사운드와 긴 배터리 수명을 자랑하는 무선 이어폰입니다. 액티브 노이즈 캐슬링 기능으로 몰입감 있는 음악 감상이 가능합니다.',
    price: '128,000원',
    emoji: '🎧',
    category: '전자제품',
    createdAt: '2024-01-08',
    isFavorite: true
  },
  {
    id: 4,
    name: '아로마 디퓨저',
    description: '자연스러운 향기로 공간을 채워주는 우드 디퓨저입니다. 타이머 기능과 LED 조명으로 분위기까지 연출할 수 있습니다.',
    price: '45,000원',
    emoji: '🕯️',
    category: '홈/리빙',
    createdAt: '2024-01-05',
    isFavorite: false
  },
  {
    id: 5,
    name: '비타민 C 세럼',
    description: '순수 비타민 C 20% 함유로 피부 톤업과 탄력 개선에 효과적입니다. 민감한 피부도 안심하고 사용할 수 있는 순한 성분으로 제작되었습니다.',
    price: '38,000원',
    emoji: '🧴',
    category: '뷰티',
    createdAt: '2024-01-03',
    isFavorite: true
  }
])

// 카테고리 목록 (동적으로 생성)
const categories = computed(() => {
  const uniqueCategories = [...new Set(myProducts.value.map(p => p.category))]
  return ['전체', ...uniqueCategories]
})

// 즐겨찾기 상품들
const favoriteProducts = computed(() => {
  return myProducts.value.filter(p => p.isFavorite)
})

// 필터된 상품 목록
const filteredProducts = computed(() => {
  let filtered = myProducts.value

  // 카테고리 필터
  if (selectedCategory.value !== '전체') {
    filtered = filtered.filter(product => product.category === selectedCategory.value)
  }

  // 정렬
  if (selectedSort.value === 'latest') {
    filtered = [...filtered].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  } else if (selectedSort.value === 'oldest') {
    filtered = [...filtered].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
  } else if (selectedSort.value === 'name') {
    filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name))
  } else if (selectedSort.value === 'price_low') {
    filtered = [...filtered].sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, ''))
      const priceB = parseInt(b.price.replace(/[^0-9]/g, ''))
      return priceA - priceB
    })
  } else if (selectedSort.value === 'price_high') {
    filtered = [...filtered].sort((a, b) => {
      const priceA = parseInt(a.price.replace(/[^0-9]/g, ''))
      const priceB = parseInt(b.price.replace(/[^0-9]/g, ''))
      return priceB - priceA
    })
  } else if (selectedSort.value === 'favorite') {
    filtered = [...filtered].sort((a, b) => (b.isFavorite ? 1 : 0) - (a.isFavorite ? 1 : 0))
  }

  return filtered
})

// 뒤로 가기
const goBack = () => {
  router.go(-1)
}

// 상품 상세 보기
const openProductDetail = (product) => {
  selectedProduct.value = product
}

// 즐겨찾기 토글
const toggleFavorite = (product) => {
  product.isFavorite = !product.isFavorite
  // TODO: API 호출로 서버에 즐겨찾기 상태 저장
}

// 정렬 적용
const applySort = () => {
  showSortModal.value = false
  // computed에서 자동으로 정렬됨
}

// 상품 수정
const editProduct = (product) => {
  // TODO: 상품 수정 페이지로 이동
  router.push(`/generate?edit=${product.id}`)
}

// 상품 공유
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

// 상품 삭제
const deleteProduct = (product) => {
  if (confirm(`"${product.name}" 상품을 삭제하시겠습니까?`)) {
    const index = myProducts.value.findIndex(p => p.id === product.id)
    if (index > -1) {
      myProducts.value.splice(index, 1)
      selectedProduct.value = null
      // TODO: API 호출로 서버에서 삭제
    }
  }
}

// 컴포넌트 마운트 시
onMounted(async () => {
  // TODO: 실제로는 API에서 내가 만든 상품 목록 로드
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
