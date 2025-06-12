import os
import requests
import logging
import time

from utils.translate import translate_language
from utils.storage import CustomUpload
from model.models import GeneratedImage
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def generate_and_save_image(product_name: str, user_id: int, db: Session) -> dict:

    api_key = os.getenv('RUNPOD_API_KEY')
    api_id = os.getenv('RUNPOD_IMAGE_ENDPOINT_ID')

    if not api_key or not api_id:
        raise ValueError("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    translated_name = translate_language(product_name)
    prompt = f"High quality product photography of {translated_name}, clean white background"

    payload = {"input": {"prompt": prompt}}
    url = f"https://api.runpod.ai/v2/{api_id}/run"
    response = requests.post(url, headers=headers, json=payload)

    def upload_and_save(image_base64: str):

        upload_service = CustomUpload()
        upload_result = upload_service.upload_inference_data(image_base64, str(user_id))

        if not upload_result["success"]:
            return {"image_base64": image_base64, "message": "이미지는 생성되었지만 저장에 실패했습니다."}

        image = GeneratedImage(
            user_id=user_id,
            product_name_ko=product_name,
            product_name_en=translated_name,
            prompt_used=prompt,
            file_url=upload_result["file_url"]
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        return {"image_base64": image_base64, "message": "이미지가 성공적으로 생성되고 저장되었습니다."}

    if response.status_code == 200:
        result = response.json()

        if "output" in result:
            return upload_and_save(result["output"].get("image", result["output"].get("image_base64", "")))

        elif "id" in result:
            task_id = result["id"]
            status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"

            while True:
                status_resp = requests.get(status_url, headers=headers).json()
                if status_resp["status"] == "COMPLETED":
                    logger.info("비동기 작업 완료 이미지 생성 완")
                    return upload_and_save(status_resp["output"].get("image", status_resp["output"].get("image_base64", "")))
                elif status_resp["status"] in ["FAILED", "CANCELLED"]:
                    raise Exception(f"작업 실패: {status_resp['status']}")
                time.sleep(2)
    else:
        logger.error(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")
        raise Exception(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")

