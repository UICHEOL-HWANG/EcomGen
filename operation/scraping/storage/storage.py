import boto3
from botocore.client import Config

import os
import logging

from datetime import datetime
from typing import Optional, Dict, Any, Union, List

import json
from io import BytesIO


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Storage:

    def __init__(self,
                 bucket_name: str,
                 endpoint_url: Optional[str] = None,
                 aws_access_key: Optional[str] = None,
                 aws_secret_key: Optional[str] = None,
                 region: str = "kr-standard",
                 service_name: str = "s3"
                 ):

        self.bucket_name = bucket_name

        aws_access_key = aws_access_key or os.getenv("ACCESS_KEY")
        aws_secret_key = aws_secret_key or os.getenv("SECRET_KEY")
        endpoint_url = endpoint_url or os.getenv("ENDPOINT_URL")
        service_name = service_name or os.getenv("SERVICE_NAME", "s3")


        if not bucket_name:
            raise ValueError("버킷 이름이 필요합니다")

        client_kwargs = {
            'service_name': service_name,
            'region_name': region,
            'config': Config(signature_version='s3v4')
        }

        if aws_access_key and aws_secret_key:
            client_kwargs.update({
                'aws_access_key_id': aws_access_key,
                'aws_secret_access_key': aws_secret_key
            })

        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url

        # 3중 구조로 지속적 검증

        self.s3 = boto3.client(**client_kwargs)
        logging.info(f"커스텀 스토리지 클라이언트 초기화 완료 (버킷: {bucket_name}, 리전: {region})")

    def uploads_data(self,
                     data: Union[Dict[str, Any], list],
                     object_key: Optional[str] = None) -> str:

        # 객체 키가 지정되지 않은 경우 타임스탬프 사용
        if object_key is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_key = f"data_{timestamp}.json"

        try:
            # 데이터를 JSON으로 변환
            binary_data = BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

            # S3에 업로드
            self.s3.upload_fileobj(
                binary_data,
                self.bucket_name,
                object_key,
                ExtraArgs={'ContentType': 'application/json'}
            )

            # 객체 URI 생성
            object_uri = f"s3://{self.bucket_name}/{object_key}"
            logging.info(f"데이터 업로드 완료: {object_uri}")
            return object_uri

        except Exception as e:
            logging.error(f"데이터 업로드 중 오류 발생: {e}")
            raise