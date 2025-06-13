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
            <h1 class="text-xl font-bold text-gray-900">내가 검색한 리포트</h1>
            <p class="text-sm text-gray-600">AI 에이전트 검색 기록</p>
          </div>
        </div>
        
        <!-- 검색 버튼 -->
        <button 
          @click="showSearchModal = true"
          class="w-10 h-10 flex items-center justify-center rounded-full border border-gray-300 hover:bg-gray-50 transition"
        >
          <span class="text-lg">🔍</span>
        </button>
      </div>
    </section>

    <!-- 통계 -->
    <section class="mb-6">
      <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-100 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ reports.length }}</div>
              <div class="text-xs text-gray-600">총 검색</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ savedReports.length }}</div>
              <div class="text-xs text-gray-600">저장됨</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ recentReports.length }}</div>
              <div class="text-xs text-gray-600">최근 7일</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 필터 탭 -->
    <section class="mb-6">
      <div class="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
        <button 
          v-for="filter in filterOptions"
          :key="filter.value"
          @click="selectedFilter = filter.value"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition flex-shrink-0',
            selectedFilter === filter.value 
              ? 'bg-purple-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ filter.label }}
        </button>
      </div>
    </section>

    <!-- 리포트 목록 -->
    <section>
      <!-- 로딩 상태 -->
      <div v-if="loading" class="space-y-4">
        <div v-for="n in 4" :key="n" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
          <div class="space-y-3">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-3 bg-gray-200 rounded w-full"></div>
            <div class="h-3 bg-gray-200 rounded w-5/6"></div>
            <div class="flex justify-between">
              <div class="h-3 bg-gray-200 rounded w-1/4"></div>
              <div class="h-3 bg-gray-200 rounded w-1/6"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 리포트 카드들 -->
      <div v-else-if="filteredReports.length > 0" class="space-y-4">
        <div 
          v-for="report in filteredReports" 
          :key="report.id"
          @click="openReport(report)"
          class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer group"
        >
          <div class="p-5">
            <!-- 질문 (굵게 표시) -->
            <h3 class="font-semibold text-gray-900 mb-3 line-clamp-2 group-hover:text-purple-600 transition-colors">
              {{ report.question }}
            </h3>
            
            <!-- 답변 미리보기 (연한 텍스트) -->
            <p class="text-gray-600 text-sm mb-4 line-clamp-3 leading-relaxed">
              {{ report.answer }}
            </p>
            
            <!-- 메타 정보 -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-500">{{ formatDate(report.createdAt) }}</span>
                <span v-if="report.isSaved" class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                  저장됨
                </span>
                <span v-if="report.category" class="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                  {{ report.category }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <button 
                  @click.stop="toggleSave(report)"
                  class="text-gray-400 hover:text-yellow-500 transition-colors"
                >
                  {{ report.isSaved ? '⭐' : '☆' }}
                </button>
                <button 
                  @click.stop="shareReport(report)"
                  class="text-gray-400 hover:text-blue-500 transition-colors"
                >
                  🔗
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">📋</div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          {{ selectedFilter === 'all' ? '아직 검색한 리포트가 없습니다' : '해당 조건의 리포트가 없습니다' }}
        </h3>
        <p class="text-gray-600 mb-4">
          AI 에이전트에게 궁금한 것을 물어보세요!
        </p>
        <button 
          @click="showSearchModal = true"
          class="inline-block px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition"
        >
          AI 에이전트 검색하기
        </button>
      </div>
    </section>

    <!-- 새 검색 모달 -->
    <div v-if="showSearchModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-900">AI 에이전트 검색</h3>
            <button @click="showSearchModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          
          <form @submit.prevent="handleSearch" class="space-y-4">
            <textarea
              v-model="searchQuery"
              placeholder="궁금한 것을 자유롭게 물어보세요..."
              rows="4"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition resize-none"
            ></textarea>
            
            <button
              type="submit"
              :disabled="!searchQuery.trim() || isSearching"
              class="w-full py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition"
            >
              {{ isSearching ? '검색 중...' : '검색하기' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- 리포트 상세 모달 -->
    <div v-if="selectedReport" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- 헤더 -->
        <div class="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-2xl">
          <div class="flex items-start justify-between">
            <div class="flex-1 pr-4">
              <h2 class="text-lg font-bold text-gray-900 mb-2">{{ selectedReport.question }}</h2>
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <span>{{ formatDate(selectedReport.createdAt) }}</span>
                <span v-if="selectedReport.category" class="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                  {{ selectedReport.category }}
                </span>
              </div>
            </div>
            <button 
              @click="selectedReport = null"
              class="text-gray-400 hover:text-gray-600 flex-shrink-0"
            >
              ✕
            </button>
          </div>
        </div>
        
        <!-- 내용 -->
        <div class="p-6">
          <div class="prose prose-sm max-w-none">
            <div class="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 class="font-semibold text-gray-900 mb-2">AI 답변</h3>
              <div class="text-gray-700 leading-relaxed whitespace-pre-line">{{ selectedReport.answer }}</div>
            </div>
          </div>
          
          <!-- 액션 버튼들 -->
          <div class="flex gap-3">
            <button 
              @click="toggleSave(selectedReport)"
              :class="[
                'flex-1 py-2 rounded-lg text-sm font-medium transition',
                selectedReport.isSaved 
                  ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ selectedReport.isSaved ? '⭐ 저장됨' : '☆ 저장하기' }}
            </button>
            <button 
              @click="shareReport(selectedReport)"
              class="flex-1 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition"
            >
              🔗 공유하기
            </button>
            <button 
              @click="deleteReport(selectedReport)"
              class="flex-1 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition"
            >
              🗑️ 삭제하기
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

const router = useRouter()

// 상태 관리
const loading = ref(true)
const selectedFilter = ref('all')
const showSearchModal = ref(false)
const selectedReport = ref(null)
const searchQuery = ref('')
const isSearching = ref(false)

// 필터 옵션
const filterOptions = ref([
  { value: 'all', label: '전체' },
  { value: 'recent', label: '최근 7일' },
  { value: 'saved', label: '저장됨' },
  { value: 'trends', label: '트렌드 분석' },
  { value: 'market', label: '시장 분석' },
  { value: 'performance', label: '성과 분석' }
])

// 검색한 리포트 데이터 (실제로는 API에서 가져올 데이터)
const reports = ref([
  {
    id: 1,
    question: "이번 달 가장 인기 있는 패션 카테고리는 무엇인가요?",
    answer: "현재 가장 인기 있는 패션 카테고리는 '미니멀 스타일'입니다.\n\n📊 분석 결과:\n• 지난달 대비 35% 성장\n• 20-30대 여성층에서 특히 인기\n• 주요 키워드: '심플', '베이직', '데일리'\n\n💡 트렌드 분석:\n1. 코로나19 이후 편안함을 추구하는 소비 패턴\n2. 재택근무 증가로 실용성 중시\n3. 지속가능한 패션에 대한 관심 증가\n\n🎯 추천 아이템:\n• 베이직 티셔츠\n• 편안한 팬츠\n• 미니멀 액세서리",
    createdAt: "2024-01-20T14:30:00Z",
    category: "트렌드 분석",
    isSaved: true
  },
  {
    id: 2,
    question: "내 상품의 예상 판매량을 어떻게 예측할 수 있나요?",
    answer: "상품의 예상 판매량은 여러 요인을 종합적으로 분석하여 예측할 수 있습니다.\n\n📈 주요 예측 요소:\n1. 시장 규모 및 경쟁 상황\n2. 타겟 고객층의 구매력\n3. 계절성 및 트렌드\n4. 가격 경쟁력\n5. 마케팅 예산 및 전략\n\n🔍 분석 방법:\n• 유사 상품의 판매 데이터 분석\n• 검색량 및 관심도 트렌드\n• 소셜미디어 언급량\n• 경쟁사 제품 성과\n\n💡 실행 가능한 팁:\n1. 작은 규모로 테스트 판매 진행\n2. A/B 테스트를 통한 최적화\n3. 고객 피드백 수집 및 반영",
    createdAt: "2024-01-19T09:15:00Z",
    category: "성과 분석",
    isSaved: false
  },
  {
    id: 3,
    question: "경쟁사 대비 우리 제품의 가격 경쟁력은 어떤가요?",
    answer: "귀하의 제품 가격을 주요 경쟁사와 비교 분석한 결과입니다.\n\n💰 가격 포지셔닝:\n• 시장 평균 대비 12% 높음\n• 프리미엄 브랜드 대비 25% 낮음\n• 가성비 제품 대비 40% 높음\n\n🎯 경쟁력 분석:\n강점:\n- 품질 대비 합리적 가격\n- 브랜드 인지도 상승\n- 고객 만족도 높음\n\n개선점:\n- 가격 투명성 개선 필요\n- 할인 혜택 확대 고려\n- 번들 상품 출시 검토\n\n📊 권장 전략:\n1. 가치 기반 마케팅 강화\n2. 차별화된 서비스 제공\n3. 단계적 가격 조정",
    createdAt: "2024-01-18T16:45:00Z",
    category: "시장 분석",
    isSaved: true
  },
  {
    id: 4,
    question: "소셜미디어 마케팅 ROI를 개선하는 방법은?",
    answer: "소셜미디어 마케팅의 ROI 개선을 위한 구체적인 전략을 제시드립니다.\n\n📱 현재 성과 분석:\n• 평균 CTR: 2.3% (업계 평균 1.9%)\n• 전환율: 0.8% (개선 필요)\n• 고객 획득 비용: 평균 대비 15% 높음\n\n🚀 개선 전략:\n1. 타겟팅 최적화\n   - 고전환 오디언스 식별\n   - 리타겟팅 강화\n   - 룩얼라이크 확대\n\n2. 콘텐츠 최적화\n   - UGC 활용 증대\n   - 인터랙티브 콘텐츠\n   - 스토리텔링 강화\n\n3. 성과 측정 개선\n   - 멀티터치 어트리뷰션\n   - LTV 기반 평가\n   - 브랜드 리프트 측정",
    createdAt: "2024-01-17T11:20:00Z",
    category: "성과 분석",
    isSaved: false
  },
  {
    id: 5,
    question: "2024년 이커머스 트렌드 전망은 어떻게 되나요?",
    answer: "2024년 이커머스 업계의 주요 트렌드를 분석해드립니다.\n\n🔮 주요 트렌드:\n\n1. AI & 개인화\n   - AI 기반 상품 추천 고도화\n   - 개인맞춤형 쇼핑 경험\n   - 챗봇 상담 서비스 확산\n\n2. 지속가능성\n   - 친환경 포장재 사용 증가\n   - 카본 뉴트럴 배송\n   - 재활용 상품 카테고리 확대\n\n3. 소셜커머스 성장\n   - 라이브 쇼핑 활성화\n   - 인플루언서 마케팅 진화\n   - 소셜 결제 시스템 도입\n\n4. 옴니채널 통합\n   - O2O 서비스 확대\n   - 매장 픽업 서비스\n   - AR/VR 쇼핑 경험\n\n💡 대응 전략:\n- 기술 투자 확대\n- 고객 데이터 활용 강화\n- 파트너십 확대",
    createdAt: "2024-01-15T13:30:00Z",
    category: "트렌드 분석",
    isSaved: true
  }
])

// computed 속성들
const savedReports = computed(() => reports.value.filter(r => r.isSaved))
const recentReports = computed(() => {
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  return reports.value.filter(r => new Date(r.createdAt) > sevenDaysAgo)
})

const filteredReports = computed(() => {
  let filtered = reports.value

  if (selectedFilter.value === 'recent') {
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    filtered = filtered.filter(r => new Date(r.createdAt) > sevenDaysAgo)
  } else if (selectedFilter.value === 'saved') {
    filtered = filtered.filter(r => r.isSaved)
  } else if (selectedFilter.value !== 'all') {
    filtered = filtered.filter(r => r.category === selectedFilter.value)
  }

  return filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

// 함수들
const goBack = () => {
  router.go(-1)
}

const openReport = (report) => {
  selectedReport.value = report
}

const toggleSave = (report) => {
  report.isSaved = !report.isSaved
  // TODO: API 호출로 서버에 저장 상태 업데이트
}

const shareReport = (report) => {
  if (navigator.share) {
    navigator.share({
      title: report.question,
      text: report.answer.substring(0, 200) + '...',
      url: window.location.href
    })
  } else {
    const shareText = `질문: ${report.question}\n\n답변: ${report.answer}`
    navigator.clipboard.writeText(shareText)
    alert('리포트가 클립보드에 복사되었습니다!')
  }
}

const deleteReport = (report) => {
  if (confirm('이 리포트를 삭제하시겠습니까?')) {
    const index = reports.value.findIndex(r => r.id === report.id)
    if (index > -1) {
      reports.value.splice(index, 1)
      selectedReport.value = null
      // TODO: API 호출로 서버에서 삭제
    }
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return

  isSearching.value = true
  
  try {
    // TODO: 실제 AI 검색 API 호출
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 임시 응답 생성
    const newReport = {
      id: Date.now(),
      question: searchQuery.value,
      answer: "AI가 분석한 답변이 여기에 표시됩니다...",
      createdAt: new Date().toISOString(),
      category: "기타",
      isSaved: false
    }
    
    reports.value.unshift(newReport)
    showSearchModal.value = false
    searchQuery.value = ''
    
    // 새로 생성된 리포트 바로 열기
    selectedReport.value = newReport
    
  } catch (error) {
    alert('검색 중 오류가 발생했습니다.')
  } finally {
    isSearching.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return '오늘'
  if (diffDays === 2) return '어제'
  if (diffDays <= 7) return `${diffDays - 1}일 전`
  
  return date.toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric'
  })
}

// 컴포넌트 마운트
onMounted(async () => {
  // TODO: 실제로는 API에서 리포트 목록 로드
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

/* prose 스타일 오버라이드 */
.prose {
  color: inherit;
}

.prose h3 {
  color: inherit;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
</style>
