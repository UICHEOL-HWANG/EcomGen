import boto3
import json
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_category_object(
        bucket_name: str,
        prefix: str,
        aws_access_key: str,
        aws_secret_key: str,
        endpoint_url: str = None,
        key_filter_prefix: str = "category_"
)-> pd.DataFrame:

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        endpoint_url=endpoint_url
    )

    #
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    objects = response.get("Contents", [])

    category_files = [
        obj["Key"] for obj in objects
        if obj["Key"].endswith('.json') and key_filter_prefix in obj['Key']
    ]

    data = []

    for key in category_files:
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            content = obj['Body'].read().decode('utf-8')
            json_data = json.loads(content)

            if isinstance(json_data, list):
                data.extend(json_data)
            elif isinstance(json_data, dict) and "products" in json_data:
                data.extend(json_data["products"])
        except Exception as e:
            logger.error(f"{key} 처리 중 오류 발생: {e}")

    df = pd.DataFrame(data)
    logger.info(f"총 {len(df)}개의 레코드가 로드되었습니다.")
    return df

def upload_json_to_s3(
    data,
    bucket_name: str,
    key: str,
    aws_access_key: str,
    aws_secret_key: str,
    endpoint_url: str = None
) -> None:
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        endpoint_url=endpoint_url
    )

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        )
        logger.info(f"✅ S3 업로드 완료: s3://{bucket_name}/{key}")
    except Exception as e:
        logger.error(f"S3 업로드 실패: {e}")
