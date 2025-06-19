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
            <h1 class="text-xl font-bold text-gray-900">내 리포트</h1>
            <p class="text-sm text-gray-600">저장된 AI 리포트 목록</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 통계 -->
    <section class="mb-6">
      <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-100 p-4">
        <div class="flex items-center justify-center">
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600">{{ reports.length }}</div>
            <div class="text-xs text-gray-600">저장된 리포트</div>
          </div>
        </div>
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
      <div v-else-if="reports.length > 0" class="space-y-4">
        <div 
          v-for="report in reports" 
          :key="report.report_id"
          @click="openReport(report)"
          class="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer group"
        >
          <div class="p-5">
            <!-- 제목 -->
            <h3 class="font-semibold text-gray-900 mb-3 line-clamp-2 group-hover:text-purple-600 transition-colors">
              {{ report.title || '제목 없음' }}
            </h3>
            
            <!-- 질문 미리보기 -->
            <p class="text-gray-600 text-sm mb-4 line-clamp-2 leading-relaxed">
              {{ extractQuery(report) }}
            </p>
            
            <!-- 메타 정보 -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-500">{{ formatDate(report.created_at) }}</span>
                <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                  AI 리포트
                </span>
              </div>
              <div class="flex items-center gap-2">
                <button 
                  @click.stop="shareReport(report)"
                  class="text-gray-400 hover:text-blue-500 transition-colors"
                >
                  🔗
                </button>
                <button 
                  @click.stop="deleteReport(report)"
                  class="text-gray-400 hover:text-red-500 transition-colors"
                >
                  🗑️
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
          저장된 리포트가 없습니다
        </h3>
        <p class="text-gray-600 mb-4">
          AI 리포트를 생성하고 저장해보세요!
        </p>
        <button 
          @click="$router.push('/report')"
          class="inline-block px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition"
        >
          새 리포트 생성하기
        </button>
      </div>
    </section>

    <!-- 리포트 상세 모달 -->
    <div v-if="selectedReport" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
      <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- 헤더 -->
        <div class="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-2xl">
          <div class="flex items-start justify-between">
            <div class="flex-1 pr-4">
              <h2 class="text-lg font-bold text-gray-900 mb-2">{{ selectedReport.title || '제목 없음' }}</h2>
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <span>{{ formatDate(selectedReport.created_at) }}</span>
                <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                  AI 리포트
                </span>
              </div>
            </div>
            <button 
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600 flex-shrink-0"
            >
              ✕
            </button>
          </div>
        </div>
        
        <!-- 내용 -->
        <div class="p-6">
          <!-- 질문 -->
          <div class="bg-blue-50 rounded-lg p-4 mb-6">
            <h3 class="font-semibold text-blue-900 mb-2">📝 질문:</h3>
            <div class="text-blue-800">{{ extractQuery(selectedReport) }}</div>
          </div>

          <!-- AI 답변 -->
          <div class="prose prose-sm max-w-none">
            <div class="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 class="font-semibold text-gray-900 mb-2">🤖 AI 답변:</h3>
              <div class="text-gray-700 leading-relaxed">
                <div v-if="selectedReport.content" v-html="formatContent(selectedReport.content)"></div>
                <div v-else class="text-gray-500 italic">리포트 내용이 비어있습니다.</div>
              </div>
            </div>
          </div>
          
          <!-- 액션 버튼들 -->
          <div class="flex gap-3">
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getReports, deleteReport as deleteReportAPI, getReport } from '@/api/reports.js'

const router = useRouter()

// 상태 관리
const loading = ref(true)
const selectedReport = ref(null)
const reports = ref([])

// 함수들
const goBack = () => {
  router.go(-1)
}

const loadReports = async () => {
  try {
    loading.value = true
    console.log('리포트 목록 로드 시작...')
    console.log('토큰 확인 (sessionStorage):', sessionStorage.getItem('token'))
    
    const response = await getReports(1, 50) // 최대 50개 로드
    console.log('리포트 목록 응답:', response)
    
    reports.value = response.reports || []
    console.log('로드된 리포트 수:', reports.value.length)
    
  } catch (error) {
    console.error('리포트 목록 조회 실패:', error)
    
    // 인증 오류인 경우 또는 401 에러
    if (error.response?.status === 401 || error.message.includes('401') || error.message.includes('authenticated')) {
      console.log('인증 오류 발생, 로그인 페이지로 이동')
      alert('로그인이 필요합니다. 로그인 페이지로 이동합니다.')
      router.push('/login')
    } else {
      alert(`리포트 목록을 불러오는데 실패했습니다: ${error.message}`)
    }
  } finally {
    loading.value = false
  }
}

const openReport = async (report) => {
  try {
    const res = await getReport(report.report_id)
    selectedReport.value = res.report
    // 모달 열릴 때 body 스크롤 블록
    document.body.style.overflow = 'hidden'
  } catch (e) {
    console.error('리포트 조회 실패:', e)
    alert('리포트를 불러오지 못했습니다.')
  }
}

const closeModal = () => {
  selectedReport.value = null
  // 모달 닫을 때 body 스크롤 복원
  document.body.style.overflow = 'auto'
}

// input_state에서 사용자 질문 추출
const extractQuery = (report) => {
  if (!report.input_state) return '질문 없음'
  
  // input_state 구조에 따라 조정
  if (typeof report.input_state === 'object' && report.input_state !== null) {
    return report.input_state.query || 
           report.input_state.prompt || 
           report.input_state.message || 
           report.input_state.text ||
           '질문 없음'
  }
  
  if (typeof report.input_state === 'string') {
    try {
      const parsed = JSON.parse(report.input_state)
      return parsed.query || parsed.prompt || parsed.message || '질문 없음'
    } catch {
      return report.input_state
    }
  }
  
  return '질문 없음'
}

const shareReport = (report) => {
  const query = extractQuery(report)
  const shareText = `📊 AI 리포트

질문: ${query}

${report.content}`
  
  if (navigator.share) {
    navigator.share({
      title: report.title || 'AI 리포트',
      text: shareText,
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(shareText)
    alert('리포트가 클립보드에 복사되었습니다!')
  }
}

const deleteReport = async (report) => {
  if (!confirm('이 리포트를 삭제하시겠습니까?')) return
  
  try {
    await deleteReportAPI(report.report_id)
    
    // 목록에서 제거
    const index = reports.value.findIndex(r => r.report_id === report.report_id)
    if (index > -1) {
      reports.value.splice(index, 1)
    }
    
    // 모달이 열려있으면 닫기
    if (selectedReport.value && selectedReport.value.report_id === report.report_id) {
      closeModal()
    }
    
    alert('리포트가 삭제되었습니다.')
  } catch (error) {
    console.error('리포트 삭제 실패:', error)
    alert('리포트 삭제에 실패했습니다.')
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

// 리포트 내용을 HTML로 포맷팅 (간단한 마크다운 처리)
const formatContent = (content) => {
  if (!content) return ''
  
  return content
    // 제목 처리 (4레벨부터 1레벨까지)
    .replace(/^#### (.*$)/gm, '<h4 class="text-base font-bold text-gray-900 mt-3 mb-2">$1</h4>')
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold text-gray-900 mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-gray-900 mt-5 mb-3">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-gray-900 mt-6 mb-4">$1</h1>')
    
    // 볼드 처리
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    
    // 리스트 처리 (간단한 - 로 시작하는 것들)
    .replace(/^- (.*$)/gm, '<li class="ml-4 mb-1">• $1</li>')
    
    // 줄바꿈 처리
    .replace(/\n\n/g, '</p><p class="mb-4">')
    .replace(/^/, '<p class="mb-4">')
    .replace(/$/, '</p>')
    
    // 빈 p 태그 제거
    .replace(/<p class="mb-4">\s*<\/p>/g, '')
    
    // li 태그들을 ul로 감싸기
    .replace(/(<li class="ml-4 mb-1">.*?<\/li>)/gs, (match) => {
      const listItems = match.match(/<li class="ml-4 mb-1">.*?<\/li>/g)
      return `<ul class="list-none mb-4">${listItems.join('')}</ul>`
    })
}

// 컴포넌트 마운트
onMounted(() => {
  loadReports()
})
</script>

<style scoped>
/* 텍스트 줄임 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* prose 스타일 오버라이드 */
.prose {
  color: inherit;
}

.prose h1, .prose h2, .prose h3 {
  color: inherit;
  margin-top: 0;
}
</style>
