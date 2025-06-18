<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <!-- 메인 콘텐츠 -->
    <div class="flex-1 px-4 py-6">
      <!-- 헤더 -->
      <section class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">🤖 AI 리포트 생성</h1>
        <p class="text-gray-600 text-sm">시장 동향, 비즈니스 분석, 전략 등 무엇이든 AI에게 물어보세요</p>
      </section>

      <!-- 생성 단계 표시 -->
      <section class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                 :class="currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'">
              1
            </div>
            <span class="text-sm font-medium text-gray-700">질문 입력</span>
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
            <span class="text-sm font-medium text-gray-700">AI 분석</span>
          </div>
        </div>
      </section>

      <!-- 1단계: 질문 입력 -->
      <section v-if="currentStep === 1" class="space-y-6 pb-20">
        <form @submit.prevent="handleGenerateReport" class="space-y-6">
          <!-- 빠른 질문 예시 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <label class="block text-lg font-semibold text-gray-900 mb-3">빠른 질문 선택</label>
            <div class="grid grid-cols-1 gap-3">
              <button 
                v-for="(question, index) in quickQuestions"
                :key="index"
                type="button"
                @click="queryForm.query = question.example"
                class="p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition"
              >
                <div class="flex items-start gap-3">
                  <span class="text-lg">{{ question.emoji }}</span>
                  <div>
                    <h3 class="font-medium text-gray-900">{{ question.title }}</h3>
                    <p class="text-sm text-gray-600 mt-1">{{ question.example }}</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- 직접 질문 입력 -->
          <div class="bg-white rounded-xl border border-gray-200 p-6">
            <label class="block text-lg font-semibold text-gray-900 mb-3">또는 직접 질문 입력 *</label>
            <textarea
              v-model="queryForm.query"
              rows="4"
              required
              placeholder="예: 2025년 가장 인기 있는 패션 트렌드는 무엇인가요? 온라인 쇼핑몰을 시작하려면 어떤 카테고리가 좋을까요?"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition resize-none"
            ></textarea>
            <p class="text-sm text-gray-500 mt-2">💡 구체적이고 명확한 질문일수록 더 정확한 답변을 받을 수 있어요</p>
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
              {{ loading ? 'AI가 분석 중...' : '🔍 AI 리포트 생성하기' }}
            </button>
          </div>
        </form>
      </section>

      <!-- 2단계: 분석 결과 -->
      <section v-if="currentStep === 2" class="space-y-6 pb-20">
        <!-- 생성된 리포트 -->
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>🤖</span>
            AI 분석 결과
          </h3>
          
          <!-- 리포트 로딩 스켈레톤 -->
          <div v-if="reportLoading" class="animate-pulse space-y-4">
            <div class="h-4 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-6 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded"></div>
            <div class="h-4 bg-gray-200 rounded w-2/3"></div>
            <div class="h-4 bg-gray-200 rounded"></div>
          </div>
          
          <!-- 생성된 리포트 내용 -->
          <div v-else-if="generatedReport" class="space-y-4">
            <!-- 질문 표시 -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 class="font-medium text-blue-900 mb-2">📝 질문:</h4>
              <p class="text-blue-800">{{ queryForm.query }}</p>
            </div>
            
            <!-- AI 답변 -->
            <div class="prose prose-sm max-w-none">
              <div class="text-gray-700 leading-relaxed" v-html="formattedReport"></div>
            </div>
            
            <!-- 웹 검색 결과가 있는 경우 -->
            <div v-if="webResults" class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 class="font-medium text-blue-900 mb-2">🌐 참고 자료:</h4>
              <div class="text-sm text-blue-800">
                <a 
                  v-for="(link, index) in webLinks" 
                  :key="index"
                  :href="link.url" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="block hover:underline mb-1"
                >
                  {{ link.title || link.url }}
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- 액션 버튼들 -->
        <div class="flex gap-3">
          <button
            @click="resetForm"
            class="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition"
          >
            새로운 질문하기
          </button>
          <button
            v-if="generatedReport"
            @click="saveReport"
            :disabled="saving"
            class="flex-1 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
          >
            {{ saving ? '저장 중...' : '💾 리포트 저장' }}
          </button>
          <button
            v-if="generatedReport"
            @click="shareReport"
            class="px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            🔗 공유
          </button>
        </div>
      </section>

      <!-- 로딩 오버레이 -->
      <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
        <div class="bg-white rounded-2xl p-8 text-center max-w-sm w-full mx-4">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 class="font-bold text-gray-900 mb-2">AI가 열심히 분석 중입니다</h3>
          <p class="text-gray-600 text-sm">{{ progressMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { generateReportAndWait } from '@/api/report.js'
import { saveReport as saveReportAPI } from '@/api/reports.js'
import { useUserStore } from '@/store/userStore'

const router = useRouter()
const userStore = useUserStore()

// 현재 단계
const currentStep = ref(1)

// 폼 데이터
const queryForm = reactive({
  query: ''
})

// 상태 관리
const loading = ref(false)
const reportLoading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const progressMessage = ref('')
const progress = ref(0)

// 생성 결과
const generatedReport = ref('')
const webResults = ref('')
const currentJobId = ref('')

// 빠른 질문 예시
const quickQuestions = [
  {
    emoji: '📈',
    title: '시장 트렌드 분석',
    example: '2025년 가장 인기 있는 상품 카테고리는 무엇인가요?'
  },
  {
    emoji: '💰',
    title: '비즈니스 전략',
    example: '온라인 쇼핑몰을 시작하려면 어떤 준비가 필요한가요?'
  },
  {
    emoji: '🎯',
    title: '마케팅 인사이트',
    example: '젊은 세대에게 어필할 수 있는 마케팅 전략은?'
  },
  {
    emoji: '🌐',
    title: '경쟁사 분석',
    example: '패션 업계 주요 경쟁사들의 최근 동향은?'
  }
]

// 리포트 텍스트 정제
const cleanedReport = computed(() => {
  if (!generatedReport.value) return ''
  
  let text = generatedReport.value.trim()
  
  // 메인 섹션 키워드로 split해서 실제 콘텐츠만 추출
  const sectionKeywords = [
    /\*\*서론[:\*\s]*/,
    /\*\*본론[:\*\s]*/,
    /\*\*결론[:\*\s]*/,
    /\*\*요약[:\*\s]*/,
    /#{1,4}\s*서론/,
    /#{1,4}\s*본론/,
    /#{1,4}\s*결론/,
    /#{1,4}\s*요약/
  ]
  
  // 가장 빠른 섹션 시작점 찾기
  let earliestIndex = text.length
  for (const pattern of sectionKeywords) {
    const match = text.match(pattern)
    if (match && match.index < earliestIndex) {
      earliestIndex = match.index
    }
  }
  
  // 섹션 시작점이 있으면 그 지점부터 사용
  if (earliestIndex < text.length) {
    text = text.substring(earliestIndex)
  }
  
  return text
    // "보고서" 중복 제거
    .replace(/^보고서\s*[-#+\s]*/, '')
    .replace(/^###\s*보고서\s*###/, '###')
    .replace(/^보고서\s*요약\s*:/, '요약:')
    
    // AI 응답 패턴 제거 (더 강력하게)
    .replace(/^.{0,100}에 대한 보고서를? 작성[^\n]*\n?/gm, '')
    .replace(/^.{0,100}보고서를? 작성[^\n]*\n?/gm, '')
    .replace(/^.{0,100}작성 요청[^\n]*\n?/gm, '')
    .replace(/^아래 내용[^\n]*\n?/gm, '')
    .replace(/^요청하신? [^\n]*\n?/gm, '')
    .replace(/^다음과 같이[^\n]*\n?/gm, '')
    .replace(/^이에 대해[^\n]*\n?/gm, '')
    .replace(/^주요 내용은 다음과 같이[^\n]*\n?/gm, '')
    .replace(/^구성되도록 부탁드립니다[^\n]*\n?/gm, '')
    .replace(/^부탁드립니다[^\n]*\n?/gm, '')
    
    // 중복되는 제목 제거
    .replace(/^\*\*서론\*\*\s*\n?\s*\*\*서론\*\*/gm, '**서론**')
    .replace(/^\*\*본론\*\*\s*\n?\s*\*\*본론\*\*/gm, '**본론**')
    
    // 반복되는 상투 패턴 제거
    .replace(/^(.{5,50})\s*\n\s*\1\s*$/gm, '$1')
    
    // 구분선 제거
    .replace(/^---+\s*$/gm, '')
    .replace(/^\*\*\*+\s*$/gm, '')
    .replace(/^={3,}\s*$/gm, '')
    
    // 빈 줄 정리 (3개 이상의 연속 줄바꿈을 2개로)
    .replace(/\n{3,}/g, '\n\n')
    
    // 시작 부분의 비어있는 마크다운 헤더 제거
    .replace(/^\s*#+\s*$/, '')
    
    .trim()
})

// 마크다운 포맷된 리포트
const formattedReport = computed(() => {
  if (!cleanedReport.value) return ''
  
  let html = cleanedReport.value
    // URL 링크를 임시로 마킹해서 보호
    .replace(/(https?:\/\/[^\s\)\]]+)/g, '<TEMP_LINK>$1</TEMP_LINK>')
    
    // 제목을 HTML 태그로 변환 (깊은 레벨부터 처리)
    .replace(/^##### (.*$)/gm, '<h5 class="text-sm font-bold text-gray-900 mt-2 mb-1">$1</h5>')
    .replace(/^#### (.*$)/gm, '<h4 class="text-base font-bold text-gray-900 mt-3 mb-2">$1</h4>')
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold text-gray-900 mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-gray-900 mt-5 mb-3">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-gray-900 mt-6 mb-4">$1</h1>')
    
    // 볼드 처리
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    
    // 숫자 리스트 처리
    .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 mb-2">$1</li>')
    
    // 일반 리스트 처리  
    .replace(/^- (.*$)/gm, '<li class="ml-4 mb-2">$1</li>')
    .replace(/^\* (.*$)/gm, '<li class="ml-4 mb-2">$1</li>')
  
  // 연속된 <li> 태그들을 <ul> 또는 <ol>로 감싸기
  html = html.replace(/(<li.*?<\/li>\s*)+/g, (match) => {
    // 원본 텍스트에서 숫자 리스트인지 확인
    const hasNumbers = /\d+\./m.test(cleanedReport.value.substring(
      cleanedReport.value.indexOf(match.replace(/<.*?>/g, '').trim())
    ))
    
    if (hasNumbers) {
      return `<ol class="list-decimal list-inside space-y-2 mb-4 pl-4">${match}</ol>`
    } else {
      return `<ul class="list-disc list-inside space-y-2 mb-4 pl-4">${match}</ul>`
    }
  })
  
  // 단락 처리
  html = html
    .replace(/\n\n/g, '</p><p class="mb-4 leading-relaxed">')
    .replace(/^/, '<p class="mb-4 leading-relaxed">')
    .replace(/$/, '</p>')
    
    // 빈 <p> 태그 제거
    .replace(/<p class="mb-4 leading-relaxed">\s*<\/p>/g, '')
    
    // 헤딩 앞뒤의 <p> 태그 정리
    .replace(/<\/p>\s*(<h[1-5])/g, '$1')
    .replace(/(<\/h[1-5]>)\s*<p[^>]*>/g, '$1')
    
    // 리스트 앞뒤의 <p> 태그 정리  
    .replace(/<\/p>\s*(<[uo]l)/g, '$1')
    .replace(/(<\/[uo]l>)\s*<p[^>]*>/g, '$1')
    
    // URL을 다시 복원하지만 숨김 처리
    .replace(/<TEMP_LINK>(.*?)<\/TEMP_LINK>/g, '<span class="text-xs text-gray-400 hidden">$1</span>')
  
  return html
})

// 웹 링크 추출
const webLinks = computed(() => {
  if (!webResults.value) return []
  
  const urlRegex = /https?:\/\/[^\s]+/g
  const urls = webResults.value.match(urlRegex) || []
  
  return urls.slice(0, 5).map(url => ({ // 최대 5개만 표시
    url: url.replace(/[),.]$/, ''), // 마지막 문장부호 제거
    title: url.includes('youtube') ? 'YouTube 영상' : 
           url.includes('sovrn') ? '소반 링크' :
           new URL(url.replace(/[),.]$/, '')).hostname
  }))
})

// 리포트 생성 처리
const handleGenerateReport = async () => {
  errorMessage.value = ''
  
  if (!queryForm.query.trim()) {
    errorMessage.value = '질문을 입력해주세요.'
    return
  }

  // 즉시 2단계로 이동 + 로딩 상태 시작
  currentStep.value = 2
  loading.value = true
  reportLoading.value = true
  progress.value = 0
  progressMessage.value = '리포트 생성을 준비하고 있습니다...'
  
  try {
    // 실제 API 호출
    const result = await generateReportAndWait(queryForm.query, (progressData) => {
      progressMessage.value = progressData.message
      progress.value = progressData.progress || 0
    })
    
    currentJobId.value = result.jobId
    
    // API 완료 후 모달 닫기
    loading.value = false
    
    // 리포트 결과 처리
    if (result.reportData) {
      generatedReport.value = result.reportData.result
      webResults.value = result.reportData.web_results
      reportLoading.value = false
    }
    
  } catch (error) {
    console.error('리포트 생성 실패:', error)
    loading.value = false
    reportLoading.value = false
    errorMessage.value = error.message || '리포트 생성 중 오류가 발생했습니다.'
    currentStep.value = 1
  }
}

// 리포트 저장
const saveReport = async () => {
  saving.value = true
  
  try {
    // 리포트 제목 생성 (질문의 첫 50자 또는 첫 줄)
    const title = queryForm.query.split('\n')[0].substring(0, 50) + 
                  (queryForm.query.length > 50 ? '...' : '')
    
    // API로 리포트 저장 (정제된 콘텐츠 사용)
    await saveReportAPI({
      title: title,
      content: cleanedReport.value,  // 정제된 콘텐츠 사용
      jobId: currentJobId.value
    })
    
    alert('리포트가 성공적으로 저장되었습니다! 💾')
    
    // 저장 후 리포트 목록으로 이동할지 물어보기
    if (confirm('저장된 리포트 목록을 보시겠습니까?')) {
      router.push('/my-reports') // MyReports 페이지로 이동
    }
    
  } catch (error) {
    console.error('리포트 저장 실패:', error)
    alert(`저장 중 오류가 발생했습니다: ${error.message}`)
  } finally {
    saving.value = false
  }
}

// 리포트 공유
const shareReport = () => {
  const shareText = `📊 AI 리포트

질문: ${queryForm.query}

${cleanedReport.value}`
  
  if (navigator.share) {
    navigator.share({
      title: 'AI 리포트 결과',
      text: shareText,
      url: window.location.href
    })
  } else {
    // 폴백: 클립보드에 복사
    navigator.clipboard.writeText(shareText)
    alert('리포트가 클립보드에 복사되었습니다! 📋')
  }
}

// 폼 리셋
const resetForm = () => {
  currentStep.value = 1
  queryForm.query = ''
  generatedReport.value = ''
  webResults.value = ''
  errorMessage.value = ''
  currentJobId.value = ''
  progress.value = 0
  progressMessage.value = ''
}
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose p {
  margin-bottom: 1rem;
}

.prose h1, .prose h2, .prose h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.prose ul, .prose ol {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.prose li {
  margin-bottom: 0.5rem;
}
</style>
