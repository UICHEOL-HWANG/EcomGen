from dto.product import ProductDescriptionRequest, ProductDescriptionResponse, ProductImageRequest, ProductImageResponse
from service.product_description_service import generate_description_and_save
from service.product_image_service import generate_image
from fastapi import APIRouter, Body, Request, HTTPException
from dotenv import load_dotenv
import logging

from core.security import get_current_user, validate_csrf
from fastapi import Depends
from model.models import ProductDescription
from model.database import get_db
from sqlalchemy.orm import Session

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generated", tags=["generate"])

@router.post("/description", response_model=ProductDescriptionResponse)
def generate_product_description(
    request: ProductDescriptionRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    raw_request: Request = None
) -> ProductDescriptionResponse:

    validate_csrf(raw_request) # CSRF 검증

    return generate_description_and_save(request.product_name, current_user["id"], db)

@router.post("/image", response_model=ProductImageResponse)
def generate_product_image(
    request: ProductImageRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    raw_request: Request = None
) -> ProductImageResponse:
    """
    제품 이미지를 생성합니다.
    """
    try:
        validate_csrf(raw_request)  # CSRF 검증
        
        logger.info(f"사용자 {current_user['id']}가 제품 '{request.product_name}'에 대한 이미지 생성을 요청했습니다.")
        
        # 이미지 생성
        result = generate_image(request.product_name)
        
        logger.info("이미지 생성 완료 (base64 형태)")
        
        return ProductImageResponse(
            image_base64=result["image_base64"],
            message=result["message"]
        )
        
    except ValueError as ve:
        logger.error(f"설정 오류: {str(ve)}")
        raise HTTPException(status_code=500, detail="서버 설정 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"이미지 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="이미지 생성 중 오류가 발생했습니다.")
