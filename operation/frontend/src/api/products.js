import axiosInstance from './axios.js'

/**
 * 내가 생성한 상품 목록 조회
 * @param {Object} params - 쿼리 파라미터
 * @param {number} params.limit - 조회할 상품 수 (기본: 50)
 * @param {number} params.offset - 건너뛸 상품 수 (기본: 0)
 * @param {string} params.category - 필터링할 카테고리 (선택사항)
 * @param {string} params.sort_by - 정렬 기준 (latest, oldest, name, price_low, price_high)
 * @returns {Promise} 상품 목록과 메타데이터
 */
export const getMyProducts = async (params = {}) => {
  try {
    const response = await axiosInstance.get('/products/my-products', { params })
    return response.data
  } catch (error) {
    console.error('내 상품 목록 조회 실패:', error)
    throw new Error(error.response?.data?.detail || '상품 목록을 불러오는데 실패했습니다.')
  }
}

/**
 * 특정 상품 상세 정보 조회
 * @param {number} productId - 상품 ID
 * @returns {Promise} 상품 상세 정보
 */
export const getMyProduct = async (productId) => {
  try {
    const response = await axiosInstance.get(`/products/my-products/${productId}`)
    return response.data
  } catch (error) {
    console.error('상품 상세 조회 실패:', error)
    throw new Error(error.response?.data?.detail || '상품 정보를 불러오는데 실패했습니다.')
  }
}

/**
 * 내가 생성한 상품의 카테고리 목록 조회
 * @returns {Promise} 카테고리 목록
 */
export const getMyProductCategories = async () => {
  try {
    const response = await axiosInstance.get('/products/categories')
    return response.data
  } catch (error) {
    console.error('카테고리 목록 조회 실패:', error)
    throw new Error(error.response?.data?.detail || '카테고리를 불러오는데 실패했습니다.')
  }
}

/**
 * 상품 삭제
 * @param {number} productId - 삭제할 상품 ID
 * @returns {Promise} 삭제 결과
 */
export const deleteMyProduct = async (productId) => {
  try {
    const response = await axiosInstance.delete(`/products/my-products/${productId}`)
    return response.data
  } catch (error) {
    console.error('상품 삭제 실패:', error)
    throw new Error(error.response?.data?.detail || '상품 삭제에 실패했습니다.')
  }
}

/**
 * 내 상품 통계 조회
 * @returns {Promise} 통계 정보
 */
export const getMyProductsStats = async () => {
  try {
    const response = await axiosInstance.get('/products/stats')
    return response.data
  } catch (error) {
    console.error('상품 통계 조회 실패:', error)
    throw new Error(error.response?.data?.detail || '통계 정보를 불러오는데 실패했습니다.')
  }
}

/**
 * 내 상품 검색
 * @param {string} query - 검색어
 * @param {number} limit - 결과 개수 제한 (기본: 20)
 * @returns {Promise} 검색 결과
 */
export const searchMyProducts = async (query, limit = 20) => {
  try {
    const response = await axiosInstance.get('/products/search', {
      params: { query, limit }
    })
    return response.data
  } catch (error) {
    console.error('상품 검색 실패:', error)
    throw new Error(error.response?.data?.detail || '상품 검색에 실패했습니다.')
  }
}

/**
 * 다른 사용자들의 추천 상품 조회
 * @param {number} limit - 조회할 추천 상품 수 (기본: 6)
 * @param {string} category - 카테고리 필터링 (선택사항)
 * @returns {Promise} 추천 상품 목록
 */
export const getRecommendedProducts = async (limit = 6, category = null) => {
  try {
    const params = { limit }
    if (category) {
      params.category = category
    }
    
    const response = await axiosInstance.get('/products/recommended', {
      params
    })
    return response.data
  } catch (error) {
    console.error('추천 상품 조회 실패:', error)
    throw new Error(error.response?.data?.detail || '추천 상품을 불러오는데 실패했습니다.')
  }
}

/**
 * 추천 상품 카테고리 목록 조회
 * @returns {Promise} 카테고리 목록
 */
export const getRecommendedProductCategories = async () => {
  try {
    const response = await axiosInstance.get('/products/recommended/categories')
    return response.data
  } catch (error) {
    console.error('추천 상품 카테고리 조회 실패:', error)
    throw new Error(error.response?.data?.detail || '카테고리를 불러오는데 실패했습니다.')
  }
}

export default {
  getMyProducts,
  getMyProduct,
  getMyProductCategories,
  deleteMyProduct,
  getMyProductsStats,
  searchMyProducts,
  getRecommendedProducts,
  getRecommendedProductCategories
}