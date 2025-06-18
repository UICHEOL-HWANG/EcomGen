import axiosInstance from './axios.js'

// 리포트 저장
export const saveReport = async (reportData) => {
  try {
    const response = await axiosInstance.post('/report/save', {
      title: reportData.title,
      content: reportData.content,  // 정제된 콘텐츠
      job_id: reportData.jobId
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || '리포트 저장에 실패했습니다.')
  }
}

// 사용자 리포트 목록 조회
export const getReports = async (page = 1, limit = 10) => {
  try {
    const response = await axiosInstance.get('/report/list', {
      params: { page, limit }
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || '리포트 목록 조회에 실패했습니다.')
  }
}

// 특정 리포트 조회
export const getReport = async (reportId) => {
  try {
    const response = await axiosInstance.get(`/report/${reportId}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || '리포트 조회에 실패했습니다.')
  }
}

// 리포트 삭제
export const deleteReport = async (reportId) => {
  try {
    const response = await axiosInstance.delete(`/report/${reportId}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || '리포트 삭제에 실패했습니다.')
  }
}
