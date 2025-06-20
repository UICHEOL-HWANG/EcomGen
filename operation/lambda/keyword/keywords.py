import time
import requests
import hashlib
import hmac
import base64
import pandas as pd
import os
import json
import logging

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Signature:

    @staticmethod
    def generate(timestamp, method, uri, secret_key):
        message = "{}.{}.{}".format(timestamp, method, uri)
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        return base64.b64encode(hash.digest()).decode()  # decode to str


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    signature = Signature.generate(timestamp, method, uri, secret_key)

    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }


def getresults(hintKeywords):

    BASE_URL = os.getenv("BASE_URL")
    API_KEY = os.getenv("API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    CUSTOMER_ID = os.getenv("CUSTOMER_ID")

    uri = '/keywordstool'
    method = 'GET'

    params = {
        'hintKeywords': hintKeywords,
        'showDetail': '1'
    }

    response = requests.get(BASE_URL + uri, params=params,
                            headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))

    response.raise_for_status()  # error 발생 시 예외 처리

    data = pd.DataFrame(response.json()['keywordList'])

    # 전처리 ">" 이거 제거 후에 숫자로 변환해주고, 월간 검색량 위주로 sort
    data["monthlyPcQcCnt"] = data["monthlyPcQcCnt"].apply(
        lambda x: int(str(x).replace("<", "").strip()) if str(x).replace("<", "").strip().isdigit() else 0
    )

    data = data.sort_values("monthlyPcQcCnt", ascending=False).reset_index(drop=True).iloc[:10][
        ["relKeyword", "monthlyPcQcCnt"]
    ]

    return data.to_dict(orient="records")


def lambda_handler(event, context):
    """Lambda 함수 핸들러 - 기존 getresults 함수를 그대로 사용"""
    
    try:
        # 디버깅용 로그 추가
        logger.info(f"Received event: {json.dumps(event)}")
        
        # 환경변수 확인
        base_url = os.getenv("BASE_URL")
        api_key = os.getenv("API_KEY")
        logger.info(f"BASE_URL: {base_url}")
        logger.info(f"API_KEY exists: {bool(api_key)}")
        
        # 이벤트에서 hintKeywords 추출
        if 'body' in event:
            # API Gateway 요청
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            hint_keywords = body.get('hintKeywords')
        else:
            # 직접 Lambda 호출
            hint_keywords = event.get('hintKeywords')
        
        logger.info(f"Extracted hintKeywords: {hint_keywords}")
        
        if not hint_keywords:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'hintKeywords is required'})
            }
        
        logger.info(f"Processing keywords: {hint_keywords}")
        
        # 기존 함수 그대로 사용
        result = getresults(hint_keywords)
        
        logger.info(f"Got result: {len(result) if result else 0} items")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'data': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
