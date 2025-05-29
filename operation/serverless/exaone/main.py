import logging
import traceback
from config.generate_text import generate_description
import runpod

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def handler(event):
    """
    Runpod Serverless 핸들러 - 텍스트 재생성

    Args:
        event: 요청 이벤트
            {
                "input": {
                    "text": "재생성할 텍스트",
                    "generation_params": {
                        "temperature": 0.8,
                        ...
                    }
                }
            }

    Returns:
        dict: 생성된 설명
            {
                "description": "재생성된 텍스트"
            }
    """
    try:
        # 입력 데이터 가져오기
        input_data = event.get("input", {})

        # 텍스트 확인
        if "text" not in input_data:
            return {
                "error": "입력에 'text' 필드가 필요합니다"
            }

        # 텍스트와 생성 파라미터 가져오기
        refine_text = input_data["text"]
        generation_params = input_data.get("generation_params", {})

        logging.info(f"텍스트 재생성 중 (길이: {len(refine_text)})")

        # 설명 생성
        generated_text = generate_description(refine_text, **generation_params)

        # 결과 반환
        return {
            "description": generated_text
        }

    except Exception as e:
        logging.error(f"핸들러 실행 중 오류 발생: {str(e)}")
        logging.error(traceback.format_exc())

        # 오류 결과 반환
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

