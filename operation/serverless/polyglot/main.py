import logging
import traceback
from config.generate_text import generate_description

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 모델 경로 (환경 변수 또는 기본값)

def handler(event):

    try:

        # 입력 데이터 가져오기
        input_data = event.get("input", {})

        # 생성 파라미터 가져오기
        generation_params = input_data.get("generation_params", {})

        # 단일 상품명 또는 상품명 목록 확인
        if "product_name" in input_data:
            # 단일 상품 처리
            product_name = input_data["product_name"]
            logging.info(f"상품 설명 생성 중: {product_name}")

            # 설명 생성
            generated_text = generate_description(product_name, **generation_params)

            # 설명 부분만 추출 (프롬프트 제외)
            if "상품 설명: " in generated_text:
                description = generated_text.split("상품 설명: ")[1].strip()
            else:
                description = generated_text

            # 결과 반환
            return {
                "description": description
            }

        elif "products" in input_data: # 여러 상품이면
            # 여러 상품 처리
            products = input_data["products"]
            results = []

            for idx, product_name in enumerate(products):
                try:
                    logging.info(f"상품 {idx + 1}/{len(products)} 처리 중: {product_name}")

                    # 설명 생성
                    generated_text = generate_description(product_name, **generation_params)

                    # 설명 부분만 추출 (프롬프트 제외)
                    if "상품 설명: " in generated_text:
                        description = generated_text.split("상품 설명: ")[1].strip()
                    else:
                        description = generated_text

                    # 결과 추가
                    results.append({
                        "product_name": product_name,
                        "description": description
                    })

                except Exception as e:
                    logging.error(f"상품 '{product_name}' 처리 중 오류: {str(e)}")
                    results.append({
                        "product_name": product_name,
                        "error": str(e)
                    })

            # 결과 반환
            return {
                "results": results
            }

        else:
            # 필수 입력 누락
            return {
                "error": "입력에 'product_name' 또는 'products' 필드가 필요합니다"
            }

    except Exception as e:
        logging.error(f"핸들러 실행 중 오류 발생: {str(e)}")
        logging.error(traceback.format_exc())

        # 오류 결과 반환
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }