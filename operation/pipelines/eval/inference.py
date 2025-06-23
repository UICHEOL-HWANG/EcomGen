import logging
import os
import time
import requests
import json
from typing import Dict, List, Optional, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_description(
    product_name: str, 
    category: str = "", 
    price: int = 0, 
    keywords: Optional[List[str]] = None, 
    tone: str = "기본",
    max_retries: int = 3,
    timeout: int = 60
) -> str:
    """
    RunPod API를 사용하여 상품 설명을 생성합니다.
    
    Args:
        product_name: 상품명
        category: 상품 카테고리
        price: 상품 가격
        keywords: 핵심 키워드 리스트
        tone: 작성 톤
        max_retries: 최대 재시도 횟수
        timeout: 작업 타임아웃(초)
        
    Returns:
        str: 생성된 상품 설명
    """
    if keywords is None:
        keywords = []
    
    # API 키 확인
    api_key = os.getenv('RUNPOD_API_KEY')
    api_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not api_id:
        logger.error("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")
        raise ValueError("API 키 또는 엔드포인트 ID가 설정되지 않았습니다.")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
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
    logger.info(f"프롬프트 생성됨: {product_name}")
    
    payload = {"input": {"prompt": prompt}}
    url = f"https://api.runpod.ai/v2/{api_id}/run"
    
    # 재시도 로직
    for retry in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            logger.info(f"RunPod 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 즉시 응답
                if "output" in result and "description" in result["output"]:
                    description = result["output"]["description"]
                    logger.info("즉시 응답에서 description 생성 완료")
                    return description
                
                # 비동기 작업
                elif "id" in result:
                    task_id = result["id"]
                    status_url = f"https://api.runpod.ai/v2/{api_id}/status/{task_id}"
                    
                    # 작업 완료 대기
                    start_time = time.time()
                    while time.time() - start_time < timeout:
                        try:
                            status_response = requests.get(status_url, headers=headers, timeout=10)
                            
                            if status_response.status_code != 200:
                                logger.warning(f"상태 확인 실패: {status_response.status_code}")
                                time.sleep(2)
                                continue
                            
                            status_data = status_response.json()
                            
                            if status_data["status"] == "COMPLETED" and "output" in status_data and "description" in status_data["output"]:
                                description = status_data["output"]["description"]
                                logger.info("비동기 작업 완료. description 생성 완료")
                                return description
                            
                            elif status_data["status"] in ["FAILED", "CANCELLED"]:
                                error_msg = status_data.get("error", "알 수 없는 오류")
                                logger.error(f"작업 실패 또는 취소됨: {status_data['status']}, 오류: {error_msg}")
                                break  # 재시도 로직으로 넘어감
                            
                            time.sleep(2)
                        except requests.exceptions.RequestException as e:
                            logger.warning(f"상태 확인 요청 실패: {str(e)}")
                            time.sleep(2)
                    
                    # 타임아웃
                    if time.time() - start_time >= timeout:
                        logger.error(f"작업 타임아웃: {task_id}")
                        break  # 재시도 로직으로 넘어감
            
            # 상태 코드 오류
            else:
                logger.error(f"API 요청 실패: {response.status_code}, 상세내용: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"요청 실패: {str(e)}")
        
        # 마지막 시도가 아니면 재시도
        if retry < max_retries - 1:
            wait_time = 2 ** retry  # 지수 백오프 (1, 2, 4초...)
            logger.info(f"재시도 중... ({retry+1}/{max_retries}), {wait_time}초 후 시도")
            time.sleep(wait_time)
    
    # 모든 시도 실패 시 오류 발생
    logger.error(f"모든 시도 실패: {product_name}")
    raise Exception(f"상품 설명 생성 실패: {product_name}")



