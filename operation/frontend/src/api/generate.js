import axiosInstance from './axios.js'

/**
 * 상품 생성 요청 (이미지 + 텍스트 통합)
 */
export const generateProduct = async (productData) => {
  try {
    const response = await axiosInstance.post('/generated/product', productData)
    return response.data
  } catch (error) {
    console.error('상품 생성 요청 실패:', error)
    throw new Error(error.response?.data?.detail || '상품 생성 요청에 실패했습니다.')
  }
}

/**
 * 작업 상태 확인
 */
export const checkGenerationStatus = async (jobId) => {
  try {
    const response = await axiosInstance.get(`/generated/status/${jobId}`)
    return response.data
  } catch (error) {
    console.error('상태 확인 실패:', error)
    throw new Error(error.response?.data?.detail || '상태 확인에 실패했습니다.')
  }
}

/**
 * 폴링을 통한 생성 완료 대기
 * @param {string} jobId - 작업 ID
 * @param {number} maxAttempts - 최대 시도 횟수 (기본: 60회)
 * @param {number} interval - 폴링 간격 (기본: 3초)
 * @returns {Promise} 생성 완료된 결과
 */
export const waitForGenerationComplete = async (jobId, maxAttempts = 60, interval = 3000) => {
  return new Promise((resolve, reject) => {
    let attempts = 0

    const poll = async () => {
      try {
        attempts++
        
        const status = await checkGenerationStatus(jobId)
        
        // 생성 완료
        if (status.completed) {
          resolve(status)
          return
        }
        
        // 최대 시도 횟수 초과
        if (attempts >= maxAttempts) {
          reject(new Error('생성 시간이 초과되었습니다. 다시 시도해주세요.'))
          return
        }
        
        // 다음 폴링 예약
        setTimeout(poll, interval)
        
      } catch (error) {
        reject(error)
      }
    }

    // 첫 번째 폴링 시작
    poll()
  })
}

/**
 * 상품 생성 및 결과 대기 (통합 함수)
 * @param {Object} productData - 상품 데이터
 * @param {Function} onProgress - 진행 상황 콜백 (선택)
 * @returns {Promise} 최종 생성 결과
 */
export const generateProductAndWait = async (productData, onProgress = null) => {
  try {
    // 1단계: 생성 요청
    onProgress?.({ step: 'request', message: '생성 요청을 보내고 있습니다...', progress: 10 })
    
    const response = await generateProduct(productData)
    const jobId = response.job_id
    
    if (!jobId) {
      throw new Error('작업 ID를 받지 못했습니다.')
    }
    
    onProgress?.({ step: 'processing', message: 'AI가 콘텐츠를 생성하고 있습니다...', progress: 20 })
    
    // 2단계: 결과 대기 (폴링)
    const result = await waitForGenerationComplete(jobId, 60, 3000)
    
    onProgress?.({ step: 'completed', message: '생성이 완료되었습니다!', progress: 100 })
    
    return {
      jobId,
      textCompleted: result.text_completed,
      imageCompleted: result.image_completed,
      textData: result.text_data,
      imageData: result.image_data,
      completed: result.completed
    }
    
  } catch (error) {
    onProgress?.({ step: 'error', message: error.message, progress: 0 })
    throw error
  }
}

export default {
  generateProduct,
  checkGenerationStatus,
  waitForGenerationComplete,
  generateProductAndWait
}
