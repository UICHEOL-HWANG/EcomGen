from model.models import Report
from dto.report import ReportGenerateRequest, ReportGenerateResponse, ReportCallbackRequest, ReportCallbackResponse, ReportSaveRequest, ReportListResponse, ReportDetailResponse
from fastapi import APIRouter, Body, Request, HTTPException, Query
from dotenv import load_dotenv
import logging
import uuid
import json

from core.security import get_current_user, validate_csrf
from fastapi import Depends
from model.database import get_db
from sqlalchemy.orm import Session
import boto3
import os
from typing import Optional

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate", response_model=ReportGenerateResponse)
def generate_report(
    request: ReportGenerateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    raw_request: Request = None
) -> ReportGenerateResponse:
    """
    리포트 생성 요청 처리
    """
    try:
        validate_csrf(raw_request)
        
        # 고유 작업 ID 생성
        job_id = f"report_{uuid.uuid4()}"
        
        logger.info(f"리포트 생성 요청 - Job ID: {job_id}, Query: {request.query[:100]}...")

        # SQS 메시지 전송
        session = boto3.session.Session(region_name="ap-northeast-2")
        sqs = session.client("sqs")
        queue_url = os.getenv("SQS_REPORT_QUEUE_URL")
        
        logger.info(f"SQS_REPORT_QUEUE_URL: {queue_url}")
        if not queue_url:
            raise HTTPException(status_code=500, detail="SQS_REPORT_QUEUE_URL 환경변수가 설정되지 않았습니다.")
        
        payload = {
            "job_id": job_id,
            "user_id": current_user["id"],
            "query": request.query
        }
        
        logger.info(f"SQS 전송 페이로드 - Job ID: {job_id}")
        
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(payload)
        )

        return ReportGenerateResponse(
            job_id=job_id,
            status="processing",
            message="리포트 생성 요청이 접수되었습니다. 잠시 후 결과를 확인할 수 있습니다."
        )
        
    except Exception as e:
        logger.error(f"리포트 생성 요청 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="리포트 생성 요청 중 오류가 발생했습니다.")


@router.post("/callback", response_model=ReportCallbackResponse)
def receive_report_callback(
    data: ReportCallbackRequest,
    db: Session = Depends(get_db)
) -> ReportCallbackResponse:
    """
    Lambda에서 리포트 생성 완료 후 콜백 받는 엔드포인트
    """
    try:
        logger.info(f"리포트 콜백 수신 - Job ID: {data.job_id}, 결과 길이: {len(data.result)} 문자")
        
        # DB 저장
        report = Report(
            user_id=data.user_id,
            run_id=data.job_id,
            input_state={"query": data.query},
            output_state={
                "result": data.result,
                "web_results": data.web_results
            }
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)

        logger.info(f"리포트 저장 완료 - Job ID: {data.job_id}, Report ID: {report.report_id}")

        return ReportCallbackResponse(message="리포트가 성공적으로 저장되었습니다.")

    except Exception as e:
        logger.error(f"리포트 콜백 저장 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="리포트 저장 중 오류가 발생했습니다.")


@router.get("/status/{job_id}")
def get_report_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    리포트 생성 상태 확인
    """
    try:
        report = db.query(Report).filter(
            Report.user_id == current_user["id"],
            Report.run_id == job_id
        ).first()
        
        if report:
            return {
                "job_id": job_id,
                "status": "completed",
                "completed": True,
                "report_data": {
                    "report_id": report.report_id,
                    "query": report.input_state.get("query"),
                    "result": report.output_state.get("result"),
                    "web_results": report.output_state.get("web_results"),
                    "created_at": report.created_at.isoformat()
                }
            }
        else:
            return {
                "job_id": job_id,
                "status": "processing",
                "completed": False,
                "report_data": None
            }
        
    except Exception as e:
        logger.error(f"리포트 상태 확인 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="상태 확인 중 오류가 발생했습니다.")


@router.post("/save")
def save_report(
    request: ReportSaveRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    리포트 저장 (정제된 콘텐츠)
    """
    try:
        # 기존 리포트가 있는지 확인 (job_id 기준)
        existing_report = None
        if request.job_id:
            existing_report = db.query(Report).filter(
                Report.user_id == current_user["id"],
                Report.job_id == request.job_id
            ).first()
        
        if existing_report:
            # 기존 리포트 업데이트
            existing_report.title = request.title
            existing_report.content = request.content
            db.commit()
            db.refresh(existing_report)
            
            return {
                "success": True,
                "id": existing_report.report_id,
                "message": "리포트가 업데이트되었습니다."
            }
        else:
            # 새 리포트 생성
            new_report = Report(
                user_id=current_user["id"],
                run_id=request.job_id or str(uuid.uuid4()),
                title=request.title,
                content=request.content,
                job_id=request.job_id
            )
            
            db.add(new_report)
            db.commit()
            db.refresh(new_report)
            
            return {
                "success": True,
                "id": new_report.report_id,
                "message": "리포트가 저장되었습니다."
            }
        
    except Exception as e:
        logger.error(f"리포트 저장 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="리포트 저장 중 오류가 발생했습니다.")


@router.get("/list", response_model=ReportListResponse)
def get_user_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자의 저장된 리포트 목록 조회
    """
    try:
        offset = (page - 1) * limit
        
        reports = db.query(Report).filter(
            Report.user_id == current_user["id"]
        ).order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
        
        report_list = []
        for report in reports:
            # input_state에서 질문 추출
            query = ""
            if report.input_state:
                if isinstance(report.input_state, dict):
                    query = report.input_state.get("query", "")
                elif isinstance(report.input_state, str):
                    try:
                        parsed = json.loads(report.input_state)
                        query = parsed.get("query", "")
                    except:
                        query = report.input_state
            
            report_list.append({
                "report_id": report.report_id,
                "title": report.title,
                "query": query,
                "created_at": report.created_at.isoformat(),
                "input_state": report.input_state
            })
        
        return ReportListResponse(reports=report_list)
        
    except Exception as e:
        logger.error(f"리포트 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="리포트 목록 조회 중 오류가 발생했습니다.")


@router.get("/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 리포트 상세 조회
    """
    try:
        report = db.query(Report).filter(
            Report.report_id == report_id,
            Report.user_id == current_user["id"]
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")
        
        # input_state에서 질문 추출
        query = ""
        if report.input_state:
            if isinstance(report.input_state, dict):
                query = report.input_state.get("query", "")
            elif isinstance(report.input_state, str):
                try:
                    parsed = json.loads(report.input_state)
                    query = parsed.get("query", "")
                except:
                    query = report.input_state
        
        return ReportDetailResponse(
            report={
                "report_id": report.report_id,
                "title": report.title,
                "query": query,
                "content": report.content,
                "created_at": report.created_at.isoformat(),
                "input_state": report.input_state
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"리포트 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="리포트 조회 중 오류가 발생했습니다.")


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    리포트 삭제
    """
    try:
        report = db.query(Report).filter(
            Report.report_id == report_id,
            Report.user_id == current_user["id"]
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="리포트를 찾을 수 없습니다.")
        
        db.delete(report)
        db.commit()
        
        return {
            "success": True,
            "message": "리포트가 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"리포트 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="리포트 삭제 중 오류가 발생했습니다.")
