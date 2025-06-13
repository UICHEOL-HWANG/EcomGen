from model.models import GeneratedImage
from utils.storage import CustomUpload
from dto.product import CombinedProductRequest, CombinedProductResponse, ProductImageCallbackRequest
from service.product_description_service import generate_description_and_save
from fastapi import APIRouter, Body, Request, HTTPException
from dotenv import load_dotenv
import logging

from core.security import get_current_user, validate_csrf
from fastapi import Depends
from model.models import ProductDescription
from model.database import get_db
from sqlalchemy.orm import Session
import boto3
import json
import os

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generated", tags=["generate"])


# 제품 설명 생성 + 이미지 생성 SQS 요청 통합 처리
from fastapi import status

@router.post("/product", response_model=CombinedProductResponse)
def generate_product_combined(
    request: CombinedProductRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    raw_request: Request = None
) -> CombinedProductResponse:
    """
    제품 설명 생성 + 이미지 생성 SQS 요청 통합 처리
    """
    try:
        validate_csrf(raw_request)

        # 1. 텍스트 설명 생성
        description_result = generate_description_and_save(
            product_name=request.product_name,
            user_id=current_user["id"],
            db=db
        )

        # 2. 이미지 생성 요청 SQS 전송
        sqs = boto3.client("sqs")
        queue_url = os.getenv("SQS_IMAGE_QUEUE_URL")

        payload = {
            "product_name": request.product_name,
            "user_id": current_user["id"]
        }

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(payload)
        )

        return CombinedProductResponse(
            description=description_result.description,
            image_message="이미지 생성 요청이 접수되었습니다. 잠시 후 자동 저장됩니다."
        )
        
    except Exception as e:
        logger.error(f"제품 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="제품 생성 중 오류가 발생했습니다.")


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

        # DB 저장
        image = GeneratedImage(
            user_id=data.user_id,
            product_name_ko=data.product_name,
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