from model.models import GeneratedImage
from utils.storage import CustomUpload
from dto.product import CombinedProductRequest, CombinedProductResponse, ProductImageCallbackRequest, ProductTextCallbackRequest, ProductTextCallbackResponse, GenerationStatusResponse
from fastapi import APIRouter, Body, Request, HTTPException
from dotenv import load_dotenv
import logging
import uuid
import json

from core.security import get_current_user, validate_csrf
from fastapi import Depends
from model.models import ProductDescription
from model.database import get_db
from sqlalchemy.orm import Session
import boto3
import os

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generated", tags=["generate"])


@router.post("/product", response_model=CombinedProductResponse)
def generate_product_combined(
    request: CombinedProductRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    raw_request: Request = None
) -> CombinedProductResponse:
    """
    제품 설명 생성 + 이미지 생성 SQS 요청 통합 처리
    """
    try:
        validate_csrf(raw_request)
        
        # 고유 작업 ID 생성
        job_id = str(uuid.uuid4())

        # 1. 텍스트 생성 요청 SQS 전송
        session = boto3.session.Session(region_name="ap-northeast-2")
        sqs = session.client("sqs")
        text_queue_url = os.getenv("SQS_TEXT_QUEUE_URL")
        
        # 디버깅: 환경변수 확인
        logger.info(f"SQS_TEXT_QUEUE_URL: {text_queue_url}")
        if not text_queue_url:
            raise HTTPException(status_code=500, detail="SQS_TEXT_QUEUE_URL 환경변수가 설정되지 않았습니다.")
        
        text_payload = {
            "job_id": job_id,
            "user_id": current_user["id"],
            "product_name": request.product_name,
            "category": request.category,
            "price": request.price,
            "keywords": request.keywords,
            "tone": request.tone
        }
        
        sqs.send_message(
            QueueUrl=text_queue_url,
            MessageBody=json.dumps(text_payload)
        )

        # 2. 이미지 생성 요청 SQS 전송
        image_queue_url = os.getenv("SQS_IMAGE_QUEUE_URL")
        
        # 디버깅: 환경변수 확인
        logger.info(f"SQS_IMAGE_QUEUE_URL: {image_queue_url}")
        if not image_queue_url:
            raise HTTPException(status_code=500, detail="SQS_IMAGE_QUEUE_URL 환경변수가 설정되지 않았습니다.")
        image_payload = {
            "job_id": job_id,
            "user_id": current_user["id"],
            "product_name": request.product_name
        }
        
        sqs.send_message(
            QueueUrl=image_queue_url,
            MessageBody=json.dumps(image_payload)
        )

        return CombinedProductResponse(
            job_id=job_id,  # 작업 ID 반환
            description="텍스트 생성 요청이 접수되었습니다. 잠시 후 자동 저장됩니다.",
            image_message="이미지 생성 요청이 접수되었습니다. 잠시 후 자동 저장됩니다."
        )
        
    except Exception as e:
        logger.error(f"제품 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 생성 중 오류가 발생했습니다.")


# 작업 상태 확인 엔드포인트 추가
@router.get("/status/{job_id}", response_model=GenerationStatusResponse)
def get_generation_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> GenerationStatusResponse:
    """
    작업 상태 확인 (폴링용)
    """
    try:
        # 텍스트 생성 완료 여부 확인
        text_result = db.query(ProductDescription).filter(
            ProductDescription.user_id == current_user["id"],
            ProductDescription.job_id == job_id
        ).first()
        
        # 이미지 생성 완료 여부 확인  
        image_result = db.query(GeneratedImage).filter(
            GeneratedImage.user_id == current_user["id"],
            GeneratedImage.job_id == job_id
        ).first()
        
        return GenerationStatusResponse(
            job_id=job_id,
            text_completed=text_result is not None,
            image_completed=image_result is not None,
            text_data={
                "description": text_result.generated_description if text_result else None  # 수정: 모델 필드명 맞춤
            } if text_result else None,
            image_data={
                "file_url": image_result.file_url if image_result else None,
                "product_name_en": image_result.product_name_en if image_result else None
            } if image_result else None,
            completed=text_result is not None and image_result is not None
        )
        
    except Exception as e:
        logger.error(f"상태 확인 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="상태 확인 중 오류가 발생했습니다.")


@router.post("/callback/image")
def receive_image_callback(
    data: ProductImageCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Lambda에서 이미지 생성 완료 후 콜백 받는 엔드포인트
    """
    try:
        # 이미지 업로드
        upload_service = CustomUpload()
        upload_result = upload_service.upload_inference_data(data.image_base64, str(data.user_id))

        if not upload_result["success"]:
            raise HTTPException(status_code=500, detail="이미지는 생성되었지만 업로드에 실패했습니다.")

        # DB 저장 (모델 필드명에 맞춤)
        image = GeneratedImage(
            user_id=data.user_id,
            job_id=data.job_id,
            product_name_ko=data.product_name_ko,
            product_name_en=data.product_name_en,
            prompt_used=data.prompt,
            file_url=upload_result["file_url"]
        )
        
        db.add(image)
        db.commit()
        db.refresh(image)

        return {"message": "이미지가 성공적으로 저장되었습니다."}
    
    except Exception as e:
        logger.error(f"이미지 콜백 저장 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 저장 중 오류가 발생했습니다.")


@router.post("/callback/text", response_model=ProductTextCallbackResponse)
def receive_text_callback(
    data: ProductTextCallbackRequest,
    db: Session = Depends(get_db)
) -> ProductTextCallbackResponse:
    """
    Lambda에서 텍스트 생성 완료 후 콜백 받는 엔드포인트
    """
    try:
        # 키워드 리스트를 JSON 문자열로 변환
        keywords_json = json.dumps(data.keywords) if data.keywords else None

        # 저장
        description_obj = ProductDescription(
            user_id=data.user_id,
            job_id=data.job_id,
            product_name=data.product_name,
            input_prompt=data.prompt,
            generated_description=data.description,
            category=data.category,
            price=data.price,
            keywords=keywords_json,
            tone=data.tone
        )
        db.add(description_obj)
        db.commit()
        db.refresh(description_obj)

        return ProductTextCallbackResponse(message="설명이 성공적으로 저장되었습니다.")

    except Exception as e:
        logger.error(f"텍스트 콜백 저장 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="설명 저장 중 오류가 발생했습니다.")