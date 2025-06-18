from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReportGenerateRequest(BaseModel):
    """리포트 생성 요청"""
    query: str


class ReportGenerateResponse(BaseModel):
    """리포트 생성 응답"""
    job_id: str
    status: str
    message: str


class ReportCallbackRequest(BaseModel):
    """Lambda에서 오는 콜백 데이터"""
    job_id: str
    user_id: int
    query: str
    result: str
    web_results: str


class ReportCallbackResponse(BaseModel):
    """콜백 응답"""
    message: str


class ReportStatusResponse(BaseModel):
    """리포트 상태 응답"""
    job_id: str
    status: str
    completed: bool
    report_data: Optional[dict] = None



class ReportSaveRequest(BaseModel):
    """리포트 저장 요청"""
    title: str
    content: str  # 정제된 마크다운 콘텐츠
    job_id: Optional[str] = None


class ReportListItem(BaseModel):
    """리포트 목록 아이템"""
    report_id: int
    title: Optional[str]
    query: str  # input_state에서 추출한 질문
    created_at: str
    input_state: Optional[Dict[str, Any]] = None


class ReportListResponse(BaseModel):
    """리포트 목록 응답"""
    reports: List[ReportListItem]


class ReportDetail(BaseModel):
    """리포트 상세 정보"""
    report_id: int
    title: Optional[str]
    query: str  # input_state에서 추출한 질문
    content: Optional[str]  # 정제된 콘텐츠
    created_at: str
    input_state: Optional[Dict[str, Any]] = None


class ReportDetailResponse(BaseModel):
    """리포트 상세 조회 응답"""
    report: ReportDetail
