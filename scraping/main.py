from config.crawl import Crawl, ListCrawl
from config.set_conifgs import headers, cookies, params
from config.category_code import all_categories

from storage.storage import Storage

import os
import time
import logging

from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import requests
from lxml import html

import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()


def main():
    final_lst = []

    # Storage 인스턴스 생성
    storage = Storage(
        bucket_name=os.getenv("S3_BUCKET_NAME"),
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key=os.getenv("ACCESS_KEY"),
        aws_secret_key=os.getenv("SECRET_KEY")
    )

    # Crawl 인스턴스 생성
    crawl = Crawl(headers=headers, cookie=cookies)

    # 레퍼러 헤더 설정
    crawl.headers.update({'referer': os.getenv("API_CATEGORY_URL")})

    # 현재 날짜 가져오기 (파일명에 사용)
    today = datetime.now().strftime("%Y%m%d")

    # ListCrawl 인스턴스 생성
    lstcrawl = ListCrawl(header=headers, cookie=cookies, params=params)

    # 각 카테고리에 대한 상품 정보 수집
    for category in tqdm(all_categories, desc="상품 데이터 수집"):
        category_products = []  # 현재 카테고리의 상품 목록

        try:
            # 카테고리별 상품 목록 가져오기
            products = lstcrawl.fetch_list_data(
                url=os.getenv("API_LIST_CONNECT_URL"),
                category=category["sub_code"]
            )

            if not products:
                logging.warning(f'카테고리 {category}에 대한 상품이 없습니다')
                continue

            # 각 상품에 대한 정보 수집
            for product in tqdm(products):
                try:
                    # 상품 상세 정보 가져오기
                    url = f'{os.getenv("API_MAIN_URL")}{product["no"]}'
                    r = requests.get(url, headers=headers, cookies=cookies)
                    r.raise_for_status()

                    # XPath로 상품 설명 텍스트 추출
                    xpaths = [
                        '//*[@id="description"]/div[1]/div/div/div[1]/div[2]/p/text()',
                        '//*[@id="description"]/div/div[6]/div[3]/div[2]/p/span/text()',
                        '//*[@id="description"]/div/div//text()'
                    ]
                    # 첫 번째 텍스트 추출 Words 태그
                    # 없으면 ktx paragraph
                    # 그래도 없으면 통째로 긁어와라

                    # 상품 설명 중 2가지 태그로 나뉘는 경우가 있어 1차 검증 후 없으면 2차 검증

                    for xpath in tqdm(xpaths):
                        result = html.fromstring(r.text).xpath(xpath)
                        if result:
                            word = " ".join(result)
                            break
                    else:
                        word = None

                    logging.info(f"{word}\n" if word else f"[{product['no']}] 상품 설명 없음\n")

                    # 상품 데이터 구성
                    data_dict = {
                        'main_code' : category["main_code"],
                        'main_category_name' : category["main_name"],
                        'sub_code' : category["sub_code"],
                        'sub_category_name' : category["sub_name"],
                        'no': product['no'],
                        'name': product['name'],
                        'image': product['list_image_url'],
                        'price': product['sales_price'],
                        'short_desc': product['short_description'],
                        'words': word
                    }

                    # 데이터 추가
                    final_lst.append(data_dict)
                    category_products.append(data_dict)
                    logging.info(f"로우데이터 수집 내용 확인 {data_dict}\n")
                    logging.info(f"상품 '{product['name']}' 데이터 수집 완료\n")

                except Exception as e:
                    logging.error(f"[{category['main_name']}:{category['sub_name']}] 상품 {product.get('no', '알 수 없음')} 처리 중 오류: {e}")

                # 과도한 요청 방지를 위한 대기
                time.sleep(random.uniform(3, 7))

            # 현재 카테고리의 상품 데이터를 S3에 저장
            if category_products:
                try:
                    storage.uploads_data(
                        data=category_products,
                        object_key=f"ecomgen/products/category_{category['main_code']}_{category['sub_code']}_{today}.json"
                    )
                    logging.info(f"카테고리 {category}의 상품 데이터({len(category_products)}개)를 S3에 저장했습니다\n")
                except Exception as e:
                    logging.error(f"카테고리 {category} 상품 데이터 S3 저장 중 오류 발생: {e}")

        except Exception as e:
            logging.error(f"[{category['main_name']}:{category['sub_name']}] 상품 처리 중 오류", exc_info=True)    # 최종 결과 로깅

    logging.info(f'총 {len(final_lst)}개의 상품 데이터를 수집했습니다')
    # 모든 상품 데이터를 S3에 저장
    try:
        # 전체 상품 데이터
        all_products_data = {
            "collection_date": today,
            "total_count": len(final_lst),
            "products": final_lst
        }

        storage.uploads_data(
            data=all_products_data,
            object_key=f"ecomgen/products/all_products_{today}.json"
        )

        logging.info(f"전체 상품 데이터({len(final_lst)}개)를 S3에 저장했습니다\n")
    except Exception as e:
        logging.error(f"전체 상품 데이터 S3 저장 중 오류 발생: {e}")

    return final_lst


if __name__ == "__main__":
    main()