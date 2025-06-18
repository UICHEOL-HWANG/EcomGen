// 리포트 API 함수들
import axiosInstance from './axios.js'

// 리포트 생성 요청
export const generateReport = async (query) => {
  try {
    const response = await axiosInstance.post('/report/generate', {
      query: query
    })
    return response.data
  } catch (error) {
    console.error('리포트 생성 요청 실패:', error)
    throw new Error(error.response?.data?.detail || '리포트 생성 요청에 실패했습니다.')
  }
}

// 리포트 상태 확인
export const getReportStatus = async (jobId) => {
  try {
    const response = await axiosInstance.get(`/report/status/${jobId}`)
    return response.data
  } catch (error) {
    console.error('리포트 상태 확인 실패:', error)
    throw new Error(error.response?.data?.detail || '상태 확인에 실패했습니다.')
  }
}

// 리포트 완료까지 대기 (폴링)
export const generateReportAndWait = async (query, onProgress = null) => {
  try {
    // 1. 리포트 생성 요청
    const generateResponse = await generateReport(query)
    const jobId = generateResponse.job_id
    
    if (onProgress) {
      onProgress({
        status: 'processing',
        message: '리포트 생성이 시작되었습니다...',
        progress: 10
      })
    }
    
    // 2. 폴링으로 완료 대기
    const maxAttempts = 120 // 10분 대기 (5초 * 120회)
    let attempts = 0
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 5000)) // 5초 대기
      attempts++
      
      const statusResponse = await getReportStatus(jobId)
      
      if (onProgress) {
        onProgress({
          status: statusResponse.status,
          message: `리포트를 생성하고 있습니다... (${attempts * 5}초 경과)`,
          progress: Math.min((attempts / 120) * 100, 95)
        })
      }
      
      if (statusResponse.completed) {
        if (onProgress) {
          onProgress({
            status: 'completed',
            message: '리포트 생성이 완료되었습니다!',
            progress: 100
          })
        }
        
        return {
          jobId: jobId,
          reportData: statusResponse.report_data
        }
      }
    }
    
    throw new Error('리포트 생성 시간이 초과되었습니다.')
    
  } catch (error) {
    console.error('리포트 생성 실패:', error)
    throw new Error(error.response?.data?.detail || error.message || '리포트 생성에 실패했습니다.')
  }
}

export default {
  generateReport,
  getReportStatus,
  generateReportAndWait
}
