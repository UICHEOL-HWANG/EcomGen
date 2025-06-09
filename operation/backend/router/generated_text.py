import os
import time
import requests
from dto.product import ProductDescriptionRequest, ProductDescriptionResponse
from fastapi import APIRouter, Body, Request
from dotenv import load_dotenv

from core.security import get_current_user, validate_csrf
from fastapi import Depends
from model.models import ProductDescription
from model.database import get_db
from sqlalchemy.orm import Session

load_dotenv()

router = APIRouter(prefix="/generated", tags=["generate"])

@router.post("/description", response_model=ProductDescriptionResponse)
def generate_product_description(
    request: ProductDescriptionRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    raw_request: Request = None  # for CSRF validation
) -> ProductDescriptionResponse:
    validate_csrf(raw_request)
    product_name = request.product_name
    api_key = os.getenv('RUNPOD_API_KEY')
    api_id = os.getenv('RUNPOD_ENDPOINT_ID')

    if not api_key or not api_id:
        raise ValueError("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    prompt = f"""
    다음 키워드를 포함하여 고객에게 매력적인 상품 설명을 작성하세요.{product_name}
    """

    payload = {"input": {"text": prompt}}

    url = f"https://api.runpod.ai/v2/{api_id}/run"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()

        def save_and_return(desc: str):
            db_desc = ProductDescription(
                product_name=product_name,
                generated_description=desc,
                user_id=current_user["id"],
                input_prompt=prompt
            )
            db.add(db_desc)
            db.commit()
            db.refresh(db_desc)
            return ProductDescriptionResponse(description=desc)

        if "output" in result:
            return save_and_return(result["output"]["description"])
        elif "id" in result:
            task_id = result["id"]
            status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"

            while True:
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()

                if status_data["status"] == "COMPLETED":
                    return save_and_return(status_data["output"]["description"])
                elif status_data["status"] in ["FAILED", "CANCELLED"]:
                    raise Exception(f"Task {status_data['status']}")
                time.sleep(2)
    else:
        raise Exception(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")