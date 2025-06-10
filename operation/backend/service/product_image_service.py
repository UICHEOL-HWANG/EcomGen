import os
import requests
import logging
import time
from utils.translate import translate_language

logger = logging.getLogger(__name__)

def generate_image(product_name: str):
    """
    제품명을 기반으로 이미지를 생성합니다.
    
    Args:
        product_name: 제품명
    
    Returns:
        dict: 생성된 이미지 base64와 메시지
    """
    api_key = os.getenv('RUNPOD_API_KEY')
    api_id = os.getenv('RUNPOD_IMAGE_ENDPOINT_ID')

    if not api_key or not api_id:
        logger.error("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")
        raise ValueError("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # 프롬프트 생성
    translated_product_name = translate_language(product_name)
    prompt = f"High quality product photography of {translated_product_name}, professional lighting, clean white background, commercial photography style, detailed, 4K resolution"
    
    logger.info(f"이미지 생성 프롬프트: {prompt}")

    payload = {
        "input": {
            "prompt": prompt
        }
    }
    
    url = f"https://api.runpod.ai/v2/{api_id}/run"
    response = requests.post(url, headers=headers, json=payload)
    logger.info(f"RunPod 응답 상태 코드: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if "output" in result:
            logger.info("즉시 응답에서 이미지 생성 완료")
            return {
                "image_base64": result["output"].get("image", result["output"].get("image_base64", "")),
                "message": "이미지가 성공적으로 생성되었습니다."
            }
        elif "id" in result:
            task_id = result["id"]
            status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"
            max_attempts = 30  # 최대 1분 대기
            attempts = 0
            
            while attempts < max_attempts:
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()
                
                if status_data["status"] == "COMPLETED":
                    logger.info("비동기 작업 완료. 이미지 생성 완료")
                    output = status_data["output"]
                    return {
                        "image_base64": output.get("image", output.get("image_base64", "")),
                        "message": "이미지가 성공적으로 생성되었습니다."
                    }
                elif status_data["status"] in ["FAILED", "CANCELLED"]:
                    logger.error(f"작업 실패 또는 취소됨: {status_data['status']}")
                    raise Exception(f"이미지 생성 작업이 실패했습니다: {status_data['status']}")
                
                attempts += 1
                time.sleep(2)
            
            raise Exception("이미지 생성 작업이 시간 초과되었습니다.")
    else:
        logger.error(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")
        raise Exception(f"API 요청 실패: {response.status_code}")
