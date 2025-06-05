from storage.object import load_category_object, upload_json_to_s3
from cleansing.cleansing_data import ProductPreprocessor
from cleansing.category_piepelines import *

from instruction_argument.generate_instructions import InstructionGenerator
from instruction_argument.batch_generate import BatchGenerator

import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from pprint import pprint # 예쁘게 출력 json format을 보고자 할 때 보면 좋을듯

load_dotenv()

def main():
    data = load_category_object(
        bucket_name=os.getenv("S3_BUCKET_NAME"),
        prefix="ecomgen/products/",
        aws_access_key=os.getenv("ACCESS_KEY"),
        aws_secret_key=os.getenv("SECRET_KEY"),
        endpoint_url=os.getenv("ENDPOINT_URL"),
    )

    preprocessor = ProductPreprocessor(stopwords=STOPWORDS)
    processed_data = preprocessor.process(data)

    instructions = InstructionGenerator(
        tone_mapping=TONE_MAPPING,
        tone_descriptions=TONE_DESCRIPTIONS,
        tone_product_name_mapping=TONE_PRODUCT_NAME_MAPPING
    )

    augmented = instructions.augment_dataset_with_tones(processed_data)

    logging.info(f"{len(augmented)}개의 증강된 인스트럭션이 생성되었습니다.")
    pprint(augmented[:3])

    # 실제 데이터 증강 생성

    generator = BatchGenerator(api_key=os.getenv("OPENAI_API_KEY"))

    batch_id = generator.create_batch(augmented)
    logging.info(f"Batch ID : {batch_id}")
    logging.info("배치 시작됨!")



    today = datetime.today().strftime("%Y%m%d")
    object_key = f"instruction/augmented_{today}.json"

    upload_json_to_s3(
        data=augmented,
        bucket_name=os.getenv("INSTRUCTION_BUCKET_NAME"),
        key=object_key,
        aws_access_key=os.getenv("ACCESS_KEY"),
        aws_secret_key=os.getenv("SECRET_KEY"),
        endpoint_url=os.getenv("ENDPOINT_URL")
    )

    logging.info(f"증강데이터 버킷 업로드 완료 경로 s3://{os.getenv('INSTRUCTION_BUCKET_NAME')}/{object_key}")

if __name__ == "__main__":
    main()