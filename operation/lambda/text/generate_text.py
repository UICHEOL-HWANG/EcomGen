import os
import json
import time
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    for record in event["Records"]:
        try:
            # SQS 메시지 파싱 (수정된 구조)
            body = json.loads(record["body"])
            
            job_id = body.get("job_id")
            user_id = body.get("user_id")
            product_name = body.get("product_name")
            category = body.get("category")
            price = body.get("price")
            keywords = body.get("keywords", [])
            tone = body.get("tone")
            

            logger.info(f"Lambda에서 받은 키워드 - Job ID: {job_id}, Keywords: {keywords}")

            if not all([job_id, user_id, product_name, category, price, tone]):
                logger.error(f"필수 필드 누락 - Job ID: {job_id}")
                continue

            logger.info(f"텍스트 생성 시작 - Job ID: {job_id}, 상품명: {product_name}")

            # 환경변수 확인
            api_key = os.getenv('RUNPOD_API_KEY')
            api_id = os.getenv('RUNPOD_TEXT_ENDPOINT_ID')
            callback_url = os.getenv('FASTAPI_TEXT_CALLBACK_URL')

            if not api_key or not api_id or not callback_url:
                raise Exception("환경변수 누락")

            # 프롬프트 생성
            keywords_str = ', '.join(keywords) if keywords else '없음'
            prompt = (
                f"당신은 상품생성 전문가입니다. 아래 조합에 따라 알맞는 상품 설명을 생성해주세요.\n"
                f"상품명: {product_name}\n"
                f"카테고리: {category}\n"
                f"가격: {price:,}원\n"
                f"핵심 키워드: {keywords_str}\n"
                f"작성 톤: {tone}\n\n"
                f"매력적이고 구매 욕구를 자극하는 상품 설명을 작성해주세요."
            )

            # RunPod API 호출
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            payload = {"input": {"text": prompt}}
            url = f"https://api.runpod.ai/v2/{api_id}/run"
            
            logger.info(f"RunPod API 호출 시작 - Job ID: {job_id}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                logger.error(f"RunPod 호출 실패: {response.status_code} - Job ID: {job_id}")
                continue

            result = response.json()
            description = ""

            # 결과 처리
            if "output" in result:
                description = result["output"].get("description", result["output"].get("text", ""))
                logger.info(f"텍스트 생성 즉시 완료 - Job ID: {job_id}")
            elif "id" in result:
                task_id = result["id"]
                status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"
                
                logger.info(f"비동기 작업 시작 - Job ID: {job_id}, Task ID: {task_id}")
                
                # 폴링으로 결과 대기 (콜드스타트 고려해서 10분으로 증가)
                max_attempts = 300  # 10분 대기 (2초 * 300회)
                for attempt in range(max_attempts):
                    time.sleep(2)
                    
                    try:
                        status_resp = requests.get(status_url, headers=headers, timeout=15)
                        status_data = status_resp.json()
                        
                        if status_data["status"] == "COMPLETED":
                            output = status_data.get("output", {})
                            description = output.get("description", output.get("text", ""))
                            logger.info(f"텍스트 생성 완료 - Job ID: {job_id}, 시도 횟수: {attempt + 1}, 소요 시간: {(attempt + 1) * 2}초")
                            break
                        elif status_data["status"] in ["FAILED", "CANCELLED"]:
                            logger.error(f"RunPod 작업 실패: {status_data['status']} - Job ID: {job_id}")
                            break
                        elif status_data["status"] in ["IN_QUEUE", "IN_PROGRESS"]:
                            # 정상적인 진행 상태, 계속 대기
                            if attempt % 30 == 0:  # 1분마다 로그
                                logger.info(f"텍스트 생성 진행 중 - Job ID: {job_id}, 상태: {status_data['status']}, 경과 시간: {(attempt + 1) * 2}초")
                        
                    except requests.exceptions.RequestException as e:
                        logger.warning(f"상태 확인 요청 실패 (재시도 중) - Job ID: {job_id}, 시도: {attempt + 1}, 오류: {str(e)}")
                        continue
                        
                if not description:
                    logger.error(f"RunPod 텍스트 생성 시간 초과 또는 실패 - Job ID: {job_id}")
                    continue
            else:
                logger.error(f"RunPod 응답에 결과 없음 - Job ID: {job_id}")
                continue

            # FastAPI 콜백 (수정된 페이로드)
            callback_payload = {
                "job_id": job_id,
                "user_id": user_id,
                "product_name": product_name,
                "category": category,
                "price": price,
                "keywords": keywords,
                "tone": tone,
                "prompt": prompt,
                "description": description
            }
            
            # 🐛 디버깅: 콜백 페이로드 키워드 로그
            logger.info(f"[DEBUG] 콜백 페이로드 키워드 - Job ID: {job_id}, Keywords: {callback_payload['keywords']}")

            # 콜백 전송 (재시도 로직 추가)
            max_callback_attempts = 3
            for callback_attempt in range(max_callback_attempts):
                try:
                    cb_resp = requests.post(callback_url, json=callback_payload, timeout=30)
                    if cb_resp.status_code == 200:
                        logger.info(f"FastAPI 콜백 성공 - Job ID: {job_id}")
                        # 🐛 디버깅: 콜백 응답 로그
                        logger.info(f"[DEBUG] 콜백 응답 - Job ID: {job_id}, Response: {cb_resp.text}")
                        break
                    else:
                        logger.error(f"FastAPI 콜백 실패 - Job ID: {job_id}, 상태코드: {cb_resp.status_code}, 응답: {cb_resp.text}")
                        if callback_attempt == max_callback_attempts - 1:
                            logger.error(f"FastAPI 콜백 최종 실패 - Job ID: {job_id}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"FastAPI 콜백 요청 실패 (재시도 중) - Job ID: {job_id}, 시도: {callback_attempt + 1}, 오류: {str(e)}")
                    if callback_attempt < max_callback_attempts - 1:
                        time.sleep(5)  # 5초 대기 후 재시도

        except Exception as e:
            logger.exception(f"텍스트 생성 처리 중 오류 발생: {str(e)}")
    
    return {"statusCode": 200, "body": "텍스트 생성 처리 완료"}