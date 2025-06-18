from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda
import logging 

def create_chaining(prompt, model, parser, stop_sequences=None):
    """
    프롬프트, 모델, 파서를 체이닝하여 실행 체인을 생성합니다.
    
    Args:
        prompt: 프롬프트 템플릿
        model: LLM 모델
        parser: 출력 파서
        stop_sequences: 생성 중단 시퀀스 리스트
    """
    # stop 조건이 있으면 모델에 바인딩 시도
    if stop_sequences:
        try:
            # bind() 시도 (OpenAI 등에서 작동)
            model_with_stop = model.bind(stop=stop_sequences)
            result = prompt | model_with_stop | parser
            logging.info("bind() 방식으로 stop 조건 적용")
        except Exception as e:
            # bind() 실패시 후처리로 stop 구현
            logging.info(f"bind() 실패, 후처리로 stop 구현: {e}")
            
            def custom_stop_parser(text):
                """텍스트에서 stop 시퀀스 제거"""
                original_text = text
                for stop in stop_sequences:
                    if stop in text:
                        text = text.split(stop)[0]
                        logging.info(f"Stop 시퀀스 '{stop}' 감지하여 텍스트 중단")
                        break
                return text.strip()
            
            # 커스텀 파서 체인에 추가
            stop_processor = RunnableLambda(custom_stop_parser)
            result = prompt | model | parser | stop_processor
            print("✅ 후처리 방식으로 stop 조건 적용")
    else:
        result = prompt | model | parser

    return result
