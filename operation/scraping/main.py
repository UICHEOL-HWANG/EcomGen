from config.crawl import Crawl, ListCrawl
from config.set_conifgs import headers, cookies, params
from config.category_code import code

from storage.storage import Storage

import os
import time
import logging

from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import requests
from lxml import html

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()


def main():
    category_lst = []
    final_lst = []
    category_data = {}  # 카테고리별 데이터를 저장할 딕셔너리

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

    # 각 카테고리에 대한 데이터 수집
    for codes in tqdm(code, desc="카테고리 데이터 수집"):
        try:
            # 카테고리 데이터 가져오기
            data = crawl.fetch_data(url=os.getenv("API_CONNECT_URL"), category=f'{codes}')

            if data:
                # 카테고리 데이터 저장
                category_data[codes] = data

                # 데이터 추가
                for categories in data:
                    category_lst.append(categories)

                # 로깅 - 첫 번째 항목 샘플 출력
                if data:
                    logging.info(f'현재 {codes} 데이터 추출중 {data[0]} 확인')
                else:
                    logging.warning(f'카테고리 {codes}에 대한 데이터가 비어 있습니다')
            else:
                logging.warning(f'카테고리 {codes}에 대한 데이터를 가져오지 못했습니다')

            # 과도한 요청 방지를 위한 대기
            time.sleep(5)

        except Exception as e:
            logging.error(f'카테고리 {codes} 처리 중 오류 발생: {e}')

    # 카테고리 데이터 수집 결과 로깅
    logging.info(f'총 {len(category_lst)}개의 카테고리 코드를 수집했습니다')

    # 카테고리 데이터를 S3에 저장
    try:
        # 카테고리 코드 목록 저장
        category_codes_data = {
            "collection_date": today,
            "categories": category_lst,
            "total_count": len(category_lst)
        }

        storage.uploads_data(
            data=category_codes_data,
            object_key=f"ecomgen/categories/category_codes_{today}.json"
        )
        logging.info(f"카테고리 코드 목록을 S3에 저장했습니다")

        # 카테고리별 상세 데이터 저장
        storage.uploads_data(
            data=category_data,
            object_key=f"ecomgen/categories/category_details_{today}.json"
        )
        logging.info(f"카테고리 상세 데이터를 S3에 저장했습니다")
    except Exception as e:
        logging.error(f"카테고리 데이터 S3 저장 중 오류 발생: {e}")

    # ListCrawl 인스턴스 생성
    lstcrawl = ListCrawl(header=headers, cookie=cookies, params=params)

    # 각 카테고리에 대한 상품 정보 수집
    for category in tqdm(category_lst, desc="상품 데이터 수집"):
        category_products = []  # 현재 카테고리의 상품 목록

        try:
            # 카테고리별 상품 목록 가져오기
            products = lstcrawl.fetch_list_data(
                url=os.getenv("API_LIST_CONNECT_URL"),
                category=category
            )

            if not products:
                logging.warning(f'카테고리 {category}에 대한 상품이 없습니다')
                continue

            # 각 상품에 대한 정보 수집
            for product in products:
                try:
                    # 상품 상세 정보 가져오기
                    url = f'{os.getenv("API_MAIN_URL")}{product["no"]}'
                    r = requests.get(url, headers=headers, cookies=cookies)
                    r.raise_for_status()

                    # XPath로 상품 설명 텍스트 추출
                    words = html.fromstring(r.text).xpath(
                        '//*[@id="description"]/div[1]/div/div/div[1]/div[2]/p/text()')
                    words = words if words else None

                    # 상품 데이터 구성
                    data_dict = {
                        'no': product['no'],
                        'name': product['name'],
                        'image': product['list_image_url'],
                        'price': product['sales_price'],
                        'short_desc': product['short_description'],
                        'words': words,
                        'category': category
                    }

                    # 데이터 추가
                    final_lst.append(data_dict)
                    category_products.append(data_dict)
                    logging.info(f"상품 '{product['name']}' 데이터 수집 완료")

                except Exception as e:
                    logging.error(f"상품 {product.get('no', '알 수 없음')} 처리 중 오류: {e}")

                # 과도한 요청 방지를 위한 대기
                time.sleep(7)

            # 현재 카테고리의 상품 데이터를 S3에 저장
            if category_products:
                try:
                    storage.uploads_data(
                        data=category_products,
                        object_key=f"ecomgen/products/category_{category}_{today}.json"
                    )
                    logging.info(f"카테고리 {category}의 상품 데이터({len(category_products)}개)를 S3에 저장했습니다")
                except Exception as e:
                    logging.error(f"카테고리 {category} 상품 데이터 S3 저장 중 오류 발생: {e}")

        except Exception as e:
            logging.error(f'카테고리 {category} 상품 처리 중 오류: {e}')

    # 최종 결과 로깅
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
        logging.info(f"전체 상품 데이터({len(final_lst)}개)를 S3에 저장했습니다")
    except Exception as e:
        logging.error(f"전체 상품 데이터 S3 저장 중 오류 발생: {e}")

    return final_lst


if __name__ == "__main__":
    main()