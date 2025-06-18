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
            # SQS 메시지 파싱 (리포트 생성용 - 최소한 구조)
            body = json.loads(record["body"])
            
            job_id = body.get("job_id")
            user_id = body.get("user_id")
            query = body.get("query")  # 리포트 주제/질문

            logger.info(f"Lambda에서 받은 리포트 요청 - Job ID: {job_id}, Query: {query[:100]}...")

            if not all([job_id, user_id, query]):
                logger.error(f"필수 필드 누락 - Job ID: {job_id}")
                continue

            logger.info(f"리포트 생성 시작 - Job ID: {job_id}")

            # 환경변수 확인
            api_key = os.getenv('RUNPOD_API_KEY')
            api_id = os.getenv('RUNPOD_AGENT_ENDPOINT_ID')  # 에이전트용 엔드포인트
            callback_url = os.getenv('FASTAPI_REPORT_CALLBACK_URL')  # 리포트 콜백 URL

            if not api_key or not api_id or not callback_url:
                raise Exception("환경변수 누락")

            # RunPod 에이전트 API 호출
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            # 에이전트용 페이로드 (query만 전송)
            payload = {
                "input": {
                    "query": query
                }
            }
            
            url = f"https://api.runpod.ai/v2/{api_id}/run"
            
            logger.info(f"RunPod 에이전트 API 호출 시작 - Job ID: {job_id}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                logger.error(f"RunPod 호출 실패: {response.status_code} - Job ID: {job_id}")
                logger.error(f"RunPod 응답: {response.text}")
                continue

            result = response.json()
            report_result = ""
            web_results = ""

            # 결과 처리
            if "output" in result:
                # 즉시 완료된 경우
                output = result["output"]
                report_result = output.get("result", "")
                web_results = output.get("web_results", "")
                logger.info(f"리포트 생성 즉시 완료 - Job ID: {job_id}")
            elif "id" in result:
                # 비동기 작업인 경우
                task_id = result["id"]
                status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"
                
                logger.info(f"비동기 리포트 작업 시작 - Job ID: {job_id}, Task ID: {task_id}")
                
                # 폴링으로 결과 대기 (리포트 생성은 더 오래 걸릴 수 있음)
                max_attempts = 600  # 20분 대기 (2초 * 600회)
                for attempt in range(max_attempts):
                    time.sleep(2)
                    
                    try:
                        status_resp = requests.get(status_url, headers=headers, timeout=15)
                        status_data = status_resp.json()
                        
                        if status_data["status"] == "COMPLETED":
                            output = status_data.get("output", {})
                            report_result = output.get("result", "")
                            web_results = output.get("web_results", "")
                            logger.info(f"리포트 생성 완료 - Job ID: {job_id}, 시도 횟수: {attempt + 1}, 소요 시간: {(attempt + 1) * 2}초")
                            break
                        elif status_data["status"] in ["FAILED", "CANCELLED"]:
                            logger.error(f"RunPod 리포트 작업 실패: {status_data['status']} - Job ID: {job_id}")
                            break
                        elif status_data["status"] in ["IN_QUEUE", "IN_PROGRESS"]:
                            # 정상적인 진행 상태, 계속 대기
                            if attempt % 30 == 0:  # 1분마다 로그
                                logger.info(f"리포트 생성 진행 중 - Job ID: {job_id}, 상태: {status_data['status']}, 경과 시간: {(attempt + 1) * 2}초")
                        
                    except requests.exceptions.RequestException as e:
                        logger.warning(f"상태 확인 요청 실패 (재시도 중) - Job ID: {job_id}, 시도: {attempt + 1}, 오류: {str(e)}")
                        continue
                        
                if not report_result:
                    logger.error(f"RunPod 리포트 생성 시간 초과 또는 실패 - Job ID: {job_id}")
                    continue
            else:
                logger.error(f"RunPod 응답에 결과 없음 - Job ID: {job_id}")
                continue

            # FastAPI 콜백 (리포트용 페이로드)
            callback_payload = {
                "job_id": job_id,
                "user_id": user_id,
                "query": query,
                "result": report_result,
                "web_results": web_results
            }
            
            logger.info(f"리포트 콜백 준비 완료 - Job ID: {job_id}, 결과 길이: {len(report_result)} 문자")

            # 콜백 전송 (재시도 로직 추가)
            max_callback_attempts = 3
            for callback_attempt in range(max_callback_attempts):
                try:
                    cb_resp = requests.post(callback_url, json=callback_payload, timeout=30)
                    if cb_resp.status_code == 200:
                        logger.info(f"FastAPI 리포트 콜백 성공 - Job ID: {job_id}")
                        logger.info(f"[DEBUG] 콜백 응답 - Job ID: {job_id}, Response: {cb_resp.text}")
                        break
                    else:
                        logger.error(f"FastAPI 리포트 콜백 실패 - Job ID: {job_id}, 상태코드: {cb_resp.status_code}, 응답: {cb_resp.text}")
                        if callback_attempt == max_callback_attempts - 1:
                            logger.error(f"FastAPI 리포트 콜백 최종 실패 - Job ID: {job_id}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"FastAPI 리포트 콜백 요청 실패 (재시도 중) - Job ID: {job_id}, 시도: {callback_attempt + 1}, 오류: {str(e)}")
                    if callback_attempt < max_callback_attempts - 1:
                        time.sleep(5)  # 5초 대기 후 재시도

        except Exception as e:
            logger.exception(f"리포트 생성 처리 중 오류 발생: {str(e)}")
    
    return {"statusCode": 200, "body": "리포트 생성 처리 완료"}
