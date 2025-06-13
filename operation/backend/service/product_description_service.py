import logging
import os
import time
import requests
import json
from sqlalchemy.orm import Session
from model.models import ProductDescription
from dto.product import ProductDescriptionResponse, ProductDescriptionRequest

logger = logging.getLogger(__name__)

def generate_description_and_save(
    request: ProductDescriptionRequest,
    user_id: int,
    db: Session
) -> ProductDescriptionResponse:
    api_key = os.getenv('RUNPOD_API_KEY')
    api_id = os.getenv('RUNPOD_ENDPOINT_ID')

    if not api_key or not api_id:
        logger.error("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")
        raise ValueError("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    prompt = (
        f"당신은 상품생성 전문가입니다. 아래 조합에 따라 알맞는 상품명을 생성해주세요."
        f"상품명: {request.product_name}\n"
        f"카테고리: {request.category}\n"
        f"가격: {request.price}원\n"
        f"핵심 키워드: {', '.join(request.keywords)}\n"
        f"작성 톤: {request.tone}\n\n"
    )

    logger.info(f"프롬프트 생성됨: {prompt}")
    payload = {"input": {"text": prompt}}
    url = f"https://api.runpod.ai/v2/{api_id}/run"
    response = requests.post(url, headers=headers, json=payload)
    logger.info(f"RunPod 응답 상태 코드: {response.status_code}")

    def save_and_return(desc: str):
        db_desc = ProductDescription(
            product_name=request.product_name,
            category=request.category,
            price=request.price,
            keywords=json.dumps(request.keywords),
            tone=request.tone,
            generated_description=desc,
            input_prompt=prompt,
            user_id=user_id
        )
        db.add(db_desc)
        db.commit()
        db.refresh(db_desc)
        return ProductDescriptionResponse(description=desc)

    if response.status_code == 200:
        result = response.json()
        if "output" in result:
            logger.info("즉시 응답에서 description 생성 완료")
            return save_and_return(result["output"]["description"])
        elif "id" in result:
            task_id = result["id"]
            status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"
            while True:
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()
                if status_data["status"] == "COMPLETED":
                    logger.info("비동기 작업 완료. description 생성 완료")
                    return save_and_return(status_data["output"]["description"])
                elif status_data["status"] in ["FAILED", "CANCELLED"]:
                    logger.error(f"작업 실패 또는 취소됨: {status_data['status']}")
                    raise Exception(f"Task {status_data['status']}")
                time.sleep(2)
    else:
        logger.error(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")
        raise Exception(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")