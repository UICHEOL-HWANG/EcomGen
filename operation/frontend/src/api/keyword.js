import axiosInstance from './axios.js'

// 키워드 추천 API
export const getKeywordRecommendations = async (hintKeywords) => {
  try {
    console.log('키워드 API 요청:', { hintKeywords })
    
    const response = await axiosInstance.post('/keyword/search', {
      hintKeywords: hintKeywords
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    console.log('키워드 API 응답:', response.data)
    return response.data
  } catch (error) {
    console.error('키워드 API 오류:', error)
    console.error('오류 응답:', error.response?.data)
    throw new Error(error.response?.data?.detail || '키워드 추천에 실패했습니다.')
  }
}
