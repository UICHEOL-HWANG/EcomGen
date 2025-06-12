import boto3
import base64
import uuid
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class CustomUpload:

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("ENDPOINT_URL"),
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY"),
            region_name=os.getenv("REGION_NAME", "ap-northeast-2")
        )
        self.bucket = os.getenv("USER_BUCKET")
        self.endpoint_url = os.getenv("ENDPOINT_URL")  # 퍼블릭 접근 URL

    def upload_inference_data(self, base64_data: str, user_id: str) -> dict:
        try:
            # Base64 디코딩
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            image_bytes = base64.b64decode(base64_data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_id = str(uuid.uuid4())[:8]
            filename = f"image_{timestamp}_{file_id}.png"
            s3_key = f"{user_id}/{filename}"

            # S3 업로드
            self.s3.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/png'
            )

            # 실제 이미지 접근 URL 생성
            file_url = f"{self.endpoint_url}/{self.bucket}/{s3_key}"

            logger.info(f"이미지 업로드 성공: {s3_key}")

            return {
                "success": True,
                "file_url": file_url,
                "s3_key": s3_key,
                "filename": filename
            }

        except Exception as e:
            logger.error(f"S3 업로드 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }