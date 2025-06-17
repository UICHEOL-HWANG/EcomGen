<template>
  <div class="px-4 py-6">
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
    <section v-if="currentStep === 1" class="space-y-6">
      <form @submit.prevent="handleGenerateProduct" class="space-y-6">
        <!-- 상품명 -->
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <label class="block text-lg font-semibold text-gray-900 mb-3">상품명 *</label>
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
          <CategorySelector v-model="productForm.category" />
        </div>

        <!-- 가격 -->
        <div class="bg-white rounded-xl border border-gray-200 p-6">
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
            <input
              v-model="keywordInput"
              @keydown.enter.prevent="addKeyword"
              type="text"
              placeholder="키워드를 입력하고 Enter를 눌러주세요"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            />
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
            {{ loading ? 'AI가 생성 중입니다...' : '🎨 AI로 상품 생성하기' }}
          </button>
        </div>
      </form>
    </section>

    <!-- 2단계: 생성 결과 -->
    <section v-if="currentStep === 2" class="space-y-6">
      <!-- 생성된 이미지 -->
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>🖼️</span>
          생성된 이미지
        </h3>
        
        <div v-if="generatedImage" class="text-center">
          <img
            :src="generatedImage.startsWith('http') ? generatedImage : `data:image/png;base64,${generatedImage}`"
            :alt="productForm.product_name"
            class="w-full max-w-sm mx-auto rounded-lg border border-gray-200 shadow-sm"
          />
        </div>
        
        <div v-else-if="imageLoading" class="text-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">이미지를 생성하고 있습니다...</p>
        </div>
      </div>

      <!-- 생성된 설명 -->
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>📝</span>
          상품 설명
        </h3>
        
        <div v-if="generatedDescription" class="prose prose-sm">
          <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ generatedDescription }}</p>
        </div>
        
        <div v-else-if="descriptionLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">설명을 생성하고 있습니다...</p>
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

    <!-- 로딩 오버레이 -->
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-8 text-center max-w-sm w-full mx-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 class="font-bold text-gray-900 mb-2">AI가 열심히 작업 중입니다</h3>
        <p class="text-gray-600 text-sm mb-4">{{ loadingMessage }}</p>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-1000"
            :style="{ width: `${loadingProgress}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { generateProductAndWait } from '@/api/generate.js'
import CategorySelector from '@/components/CategorySelector.vue'
import ToneSelector from '@/components/ToneSelector.vue'

const router = useRouter()

// 현재 단계
const currentStep = ref(1)

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

// 상태 관리
const loading = ref(false)
const imageLoading = ref(false)
const descriptionLoading = ref(false)
const saving = ref(false)
const errorMessage = ref('')

const loadingMessage = ref('')
const loadingProgress = ref(0)

// 생성 결과
const generatedImage = ref('')
const generatedDescription = ref('')
const currentJobId = ref('')

// 키워드 추가
const addKeyword = () => {
  const keyword = keywordInput.value.trim()
  if (keyword && !productForm.keywords.includes(keyword) && productForm.keywords.length < 5) {
    productForm.keywords.push(keyword)
    keywordInput.value = ''
  }
}

// 키워드 제거
const removeKeyword = (index) => {
  productForm.keywords.splice(index, 1)
}

const handleGenerateProduct = async () => {
  errorMessage.value = ''
  
  // 폼 검증
  if (!productForm.product_name || !productForm.category || !productForm.price || !productForm.tone) {
    errorMessage.value = '필수 항목을 모두 입력해주세요.'
    return
  }

  loading.value = true
  loadingProgress.value = 0
  currentStep.value = 2
  imageLoading.value = true
  descriptionLoading.value = true

  try {
    // 실제 API 호출
    const result = await generateProductAndWait(productForm, (progress) => {
      loadingMessage.value = progress.message
      loadingProgress.value = progress.progress
      
      // 단계별 로딩 상태 업데이트
      if (progress.step === 'processing') {
        if (progress.progress >= 50) {
          loadingMessage.value = '이미지를 생성하고 있습니다...'
        } else {
          loadingMessage.value = '설명을 생성하고 있습니다...'
        }
      }
    })
    
    currentJobId.value = result.jobId
    
    // 텍스트 결과 처리
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
    
    loadingMessage.value = '생성 완료!'
    loadingProgress.value = 100
    
    setTimeout(() => {
      loading.value = false
    }, 1000)
    
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
