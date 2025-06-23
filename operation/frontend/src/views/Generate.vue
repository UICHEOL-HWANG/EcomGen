<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <!-- 메인 콘텐츠 -->
    <div class="flex-1 px-4 py-6">
      <!-- 헤더 -->
      <section class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">🎨 AI 상품 생성</h1>
        <p class="text-gray-600 text-sm">상품명만 입력하면 AI가 이미지와 설명을 자동으로 생성해드립니다</p>
      </section>

      <!-- 생성 단계 표시 -->
      <section class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                 :class="currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'">
              1
            </div>
            <span class="text-sm font-medium text-gray-700">상품 정보</span>
          </div>
          <div class="flex-1 h-1 mx-3 bg-gray-200 rounded">
            <div class="h-1 bg-blue-600 rounded transition-all duration-500"
                 :style="{ width: currentStep >= 2 ? '100%' : '0%' }"></div>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                 :class="currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'">
              2
            </div>
            <span class="text-sm font-medium text-gray-700">AI 생성</span>
          </div>
        </div>
      </section>

      <!-- 1단계: 상품 정보 입력 -->
      <section v-if="currentStep === 1" class="space-y-6 pb-20">
        <form @submit.prevent="handleGenerateProduct" class="space-y-6">
          <!-- 상품명 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-3">
              <label class="block text-lg font-semibold text-gray-900">상품명 *</label>
              <button 
                @click="openKeywordModal" 
                type="button"
                class="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full hover:bg-purple-200 transition"
              >
                🔍 키워드 추천
              </button>
            </div>
            <input
              v-model="productForm.product_name"
              type="text"
              required
              placeholder="예: 미니멀 화이트 스니커즈"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
          </div>

          <!-- 카테고리 선택기 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <CategorySelector v-model="productForm.category" @category-selected="onCategorySelected" />
          </div>

          <!-- 가격 -->
          <div ref="priceSection" class="bg-white rounded-xl border border-gray-200 p-6">
            <label class="block text-lg font-semibold text-gray-900 mb-3">예상 가격 *</label>
            <div class="relative">
              <input
                v-model.number="productForm.price"
                type="number"
                required
                min="0"
                step="1000"
                placeholder="50000"
                class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
              <span class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500">원</span>
            </div>
          </div>

          <!-- 키워드 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <label class="block text-lg font-semibold text-gray-900 mb-3">키워드 (선택사항)</label>
            <div class="space-y-3">
              <div class="flex gap-2">
                <input
                  v-model="keywordInput"
                  @keydown.enter.prevent="addKeyword"
                  type="text"
                  placeholder="키워드를 입력하세요 (쉼표로 구분 가능: 맛있는,신선한)"
                  class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                />
                <button 
                  @click="addKeyword" 
                  type="button"
                  class="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  추가
                </button>
              </div>
              <div v-if="productForm.keywords.length > 0" class="flex flex-wrap gap-2">
                <span
                  v-for="(keyword, index) in productForm.keywords"
                  :key="index"
                  class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {{ keyword }}
                  <button @click="removeKeyword(index)" type="button" class="hover:text-blue-600">×</button>
                </span>
              </div>
            </div>
          </div>

          <!-- 톤 선택기 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <ToneSelector v-model="productForm.tone" />
          </div>

          <!-- 에러 메시지 -->
          <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-xl">
            <p class="text-sm text-red-600">{{ errorMessage }}</p>
          </div>

          <!-- 생성 버튼 -->
          <div class="pt-4">
            <button
              type="submit"
              :disabled="loading"
              class="w-full py-4 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition disabled:opacity-50 text-lg"
            >
              {{ loading ? 'AI가 생성 중...' : '🎨 AI로 상품 생성하기' }}
            </button>
          </div>
        </form>
      </section>

      <!-- 2단계: 생성 결과 -->
      <section v-if="currentStep === 2" class="space-y-6 pb-20">
        <!-- 생성된 이미지 -->
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>🖼️</span>
            생성된 이미지
          </h3>
          
          <!-- 이미지 로딩 스켈레톤 -->
          <div v-if="imageLoading" class="animate-pulse">
            <div class="w-full max-w-sm mx-auto h-64 bg-gray-200 rounded-lg"></div>
            <div class="text-center mt-4">
              <div class="h-4 bg-gray-200 rounded w-48 mx-auto mb-2"></div>
              <div class="h-3 bg-gray-200 rounded w-32 mx-auto"></div>
            </div>
          </div>
          
          <!-- 생성된 이미지 -->
          <div v-else-if="generatedImage" class="text-center">
            <img
              :src="generatedImage.startsWith('http') ? generatedImage : `data:image/png;base64,${generatedImage}`"
              :alt="productForm.product_name"
              class="w-full max-w-sm mx-auto rounded-lg border border-gray-200 shadow-sm"
            />
          </div>
        </div>

        <!-- 생성된 설명 -->
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>📝</span>
            상품 설명
          </h3>
          
          <!-- 설명 로딩 스켈레톤 -->
          <div v-if="descriptionLoading" class="animate-pulse space-y-3">
            <div class="h-4 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
          
          <!-- 생성된 설명 -->
          <div v-else-if="generatedDescription" class="prose prose-sm">
            <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ cleanDescription }}</p>
          </div>
        </div>

        <!-- 액션 버튼들 -->
        <div class="flex gap-3">
          <button
            @click="resetForm"
            class="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
          >
            다시 생성하기
          </button>
          <button
            v-if="generatedImage && generatedDescription"
            @click="saveProduct"
            :disabled="saving"
            class="flex-1 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
          >
            {{ saving ? '내 상품으로 이동 중...' : '내 상품 보기' }}
          </button>
        </div>
      </section>

      <!-- 로딩 오버레이 (게이지바 제거된 버전) -->
      <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
        <div class="bg-white rounded-2xl p-8 text-center max-w-sm w-full mx-4">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 class="font-bold text-gray-900 mb-2">AI가 열심히 작업 중입니다</h3>
          <p class="text-gray-600 text-sm">상품을 생성하고 있습니다...</p>
        </div>
      </div>

      <!-- 키워드 추천 모달 -->
      <div v-if="showKeywordModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
        <div class="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-y-auto">
          <!-- 모달 헤더 -->
          <div class="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-2xl">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900">🔍 키워드 추천</h3>
              <button 
                @click="closeKeywordModal"
                class="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <p class="text-sm text-gray-600 mt-2">키워드를 입력하면 관련 추천 키워드를 제공합니다</p>
          </div>
          
          <!-- 모달 내용 -->
          <div class="p-6">
            <!-- 키워드 입력 -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">키워드 입력</label>
              <div class="flex gap-2">
                <input
                  v-model="keywordQuery"
                  @keydown.enter.prevent="searchKeywords"
                  type="text"
                  placeholder="예: 신발, 스니커즈, 운동화"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none"
                />
                <button 
                  @click="searchKeywords"
                  :disabled="keywordLoading || !keywordQuery.trim()"
                  class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                >
                  검색
                </button>
              </div>
            </div>

            <!-- 로딩 상태 -->
            <div v-if="keywordLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-3"></div>
              <p class="text-gray-600 text-sm">키워드를 분석하고 있습니다...</p>
            </div>

            <!-- 추천 키워드 목록 -->
            <div v-else-if="recommendedKeywords.length > 0" class="space-y-3">
              <h4 class="font-medium text-gray-900 mb-3">📊 추천 키워드 (월간 검색량)</h4>
              <div class="space-y-2 max-h-64 overflow-y-auto">
                <div 
                  v-for="keyword in recommendedKeywords" 
                  :key="keyword.relKeyword"
                  @click="selectKeyword(keyword.relKeyword)"
                  class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-purple-50 hover:border-purple-300 cursor-pointer transition"
                >
                  <span class="font-medium text-gray-900">{{ keyword.relKeyword }}</span>
                  <span class="text-sm text-gray-500">{{ formatSearchVolume(keyword.monthlyPcQcCnt) }}</span>
                </div>
              </div>
            </div>

            <!-- 빈 상태 -->
            <div v-else-if="keywordSearched && recommendedKeywords.length === 0" class="text-center py-8">
              <div class="text-4xl mb-3">🔍</div>
              <p class="text-gray-600">추천할 키워드가 없습니다.</p>
              <p class="text-gray-500 text-sm">다른 키워드로 검색해보세요.</p>
            </div>

            <!-- 초기 상태 -->
            <div v-else class="text-center py-8">
              <div class="text-4xl mb-3">💡</div>
              <p class="text-gray-600">키워드를 입력하고 검색 버튼을 눌러보세요!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { generateProductAndWait } from '@/api/generate.js'
import { getKeywordRecommendations } from '@/api/keyword.js'
import CategorySelector from '@/components/CategorySelector.vue'
import ToneSelector from '@/components/ToneSelector.vue'

const router = useRouter()

// 현재 단계
const currentStep = ref(1)

// 예상가격 섹션 ref
const priceSection = ref(null)

// 폼 데이터
const productForm = reactive({
  product_name: '',
  category: '',
  price: null,
  keywords: [],
  tone: ''
})

// 키워드 입력
const keywordInput = ref('')

// 키워드 추천 관련 상태
const showKeywordModal = ref(false)
const keywordQuery = ref('')
const keywordLoading = ref(false)
const keywordSearched = ref(false)
const recommendedKeywords = ref([])

// 상태 관리
const loading = ref(false)
const imageLoading = ref(false)
const descriptionLoading = ref(false)
const saving = ref(false)
const errorMessage = ref('')

// 생성 결과
const generatedImage = ref('')
const generatedDescription = ref('')
const currentJobId = ref('')

// 🧹 텍스트 정제 함수
const cleanDescription = computed(() => {
  if (!generatedDescription.value) return ''
  
  return generatedDescription.value
    .trim()
    // 문서 시작의 "보고서" + 구분자 패턴 제거
    .replace(/^보고서\s*[-#+\s]*/, '')
    // 추가 정제 규칙들
    .replace(/^###\s*보고서\s*###/, '###')
    .replace(/^보고서\s*요약\s*:/, '요약:')
    .trim()
})

// 카테고리 선택 시 스크롤 처리
const onCategorySelected = () => {
  // 카테고리 선택 후 예상가격 섹션으로 부드럽게 스크롤
  setTimeout(() => {
    if (priceSection.value) {
      priceSection.value.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  }, 100) // 짧은 딜레이로 DOM 업데이트 대기
}

// 키워드 추가
const addKeyword = () => {
  const inputValue = keywordInput.value.trim()
  
  if (!inputValue) {
    return
  }
  
  // 쉼표로 분리하여 여러 키워드 처리
  const keywords = inputValue.split(',').map(k => k.trim()).filter(k => k.length > 0)
  
  let addedCount = 0
  for (const keyword of keywords) {
    if (!productForm.keywords.includes(keyword) && productForm.keywords.length < 5) {
      productForm.keywords.push(keyword)
      addedCount++
    }
    
    if (productForm.keywords.length >= 5) {
      break
    }
  }
  
  if (addedCount > 0) {
    keywordInput.value = ''
  }
}

// 키워드 제거
const removeKeyword = (index) => {
  productForm.keywords.splice(index, 1)
}

// 키워드 추천 모달 열기
const openKeywordModal = () => {
  showKeywordModal.value = true
  keywordQuery.value = ''
  recommendedKeywords.value = []
  keywordSearched.value = false
  document.body.style.overflow = 'hidden'
}

// 키워드 추천 모달 닫기
const closeKeywordModal = () => {
  showKeywordModal.value = false
  document.body.style.overflow = 'auto'
}

// 키워드 검색
const searchKeywords = async () => {
  if (!keywordQuery.value.trim()) return
  
  keywordLoading.value = true
  keywordSearched.value = false
  
  try {
    const keywords = await getKeywordRecommendations(keywordQuery.value.trim())
    recommendedKeywords.value = keywords || []
    keywordSearched.value = true
  } catch (error) {
    console.error('키워드 검색 실패:', error)
    recommendedKeywords.value = []
    keywordSearched.value = true
    alert('키워드 검색에 실패했습니다. 다시 시도해주세요.')
  } finally {
    keywordLoading.value = false
  }
}

// 키워드 선택
const selectKeyword = (keyword) => {
  productForm.product_name = keyword
  closeKeywordModal()
}

// 검색량 포맷팅
const formatSearchVolume = (volume) => {
  if (volume >= 1000000) {
    return `${Math.floor(volume / 100000) / 10}M`
  } else if (volume >= 1000) {
    return `${Math.floor(volume / 100) / 10}K`
  } else {
    return volume.toString()
  }
}

const handleGenerateProduct = async () => {
  errorMessage.value = ''
  
  // 폼 검증
  if (!productForm.product_name || !productForm.category || !productForm.price || !productForm.tone) {
    errorMessage.value = '필수 항목을 모두 입력해주세요.'
    return
  }

  // 즐시 2단계로 이동 + 로딩 상태 시작
  currentStep.value = 2
  loading.value = true  // 모달 표시
  imageLoading.value = true  // 스켈레톤 표시
  descriptionLoading.value = true  // 스켈레톤 표시
  
  try {
    // 실제 API 호출
    const result = await generateProductAndWait(productForm, (progress) => {
      // 진행 상황 로깅만 유지
      console.log('생성 진행:', progress.message)
    })
    
    currentJobId.value = result.jobId
    
    // API 완료 후 모달 닫기
    loading.value = false
    
    // 텍스트 결과 처리 (원본 저장, 정제는 computed에서)
    if (result.textData && result.textData.description) {
      generatedDescription.value = result.textData.description
      descriptionLoading.value = false
    }
    
    // 이미지 결과 처리  
    if (result.imageData && result.imageData.file_url) {
      // S3 URL을 직접 사용
      generatedImage.value = result.imageData.file_url
      imageLoading.value = false
    }
    
  } catch (error) {
    console.error('생성 실패:', error)
    loading.value = false
    imageLoading.value = false
    descriptionLoading.value = false
    errorMessage.value = error.message || '생성 중 오류가 발생했습니다.'
    currentStep.value = 1
  }
}

const saveProduct = async () => {
  saving.value = true
  
  try {
    // 상품이 이미 DB에 저장되어 있으므로 별도 저장 없이 바로 이동
    console.log('상품이 생성되었습니다:', {
      jobId: currentJobId.value,
      productName: productForm.product_name
    })
    
    // 내가 만든 상품 페이지로 이동
    router.push('/my-products')
  } catch (error) {
    errorMessage.value = '이동 중 오류가 발생했습니다.'
  } finally {
    saving.value = false
  }
}

// 폼 리셋
const resetForm = () => {
  currentStep.value = 1
  productForm.product_name = ''
  productForm.category = ''
  productForm.price = null
  productForm.keywords = []
  productForm.tone = ''
  generatedImage.value = ''
  generatedDescription.value = ''
  errorMessage.value = ''
  currentJobId.value = ''
}
</script>
