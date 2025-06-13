import os
import requests
import logging
import json
import time 

from utils.translate import translate_language

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            product_name = body["product_name"]
            user_id = body["user_id"]

            api_key = os.getenv('RUNPOD_API_KEY')
            api_id = os.getenv('RUNPOD_IMAGE_ENDPOINT_ID')
            callback_url = os.getenv('FASTAPI_IMAGE_CALLBACK_URL')

            if not api_key or not api_id or not callback_url:
                raise ValueError("환경변수가 설정되지 않았습니다.")

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            translated_name = translate_language(product_name)
            prompt = f"High quality product photography of {translated_name}, clean white background"

            payload = {"input": {"prompt": prompt}}
            url = f"https://api.runpod.ai/v2/{api_id}/run"
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                logger.error(f"RunPod 호출 실패: {response.status_code}")
                continue

            result = response.json()

            if "output" in result:
                image_base64 = result["output"].get("image", result["output"].get("image_base64", ""))
            elif "id" in result:
                task_id = result["id"]
                status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"

                while True:
                    status_resp = requests.get(status_url, headers=headers).json()
                    if status_resp["status"] == "COMPLETED":
                        image_base64 = status_resp["output"].get("image", status_resp["output"].get("image_base64", ""))
                        break
                    elif status_resp["status"] in ["FAILED", "CANCELLED"]:
                        logger.error(f"RunPod 작업 실패: {status_resp['status']}")
                        return
                    time.sleep(2)
            else:
                logger.error("RunPod 응답에 이미지 결과 없음")
                return

            # FastAPI 콜백
            callback_payload = {
                "user_id": user_id,
                "product_name_ko": product_name,
                "product_name_en": translated_name,
                "prompt": prompt,
                "image_base64": image_base64
            }

            cb_resp = requests.post(callback_url, json=callback_payload)
            if cb_resp.status_code != 200:
                logger.error(f"FastAPI 콜백 실패: {cb_resp.status_code}, 내용: {cb_resp.text}")
            else:
                logger.info("FastAPI 콜백 성공")

        except Exception as e:
            logger.exception(f"처리 중 오류 발생: {str(e)}")