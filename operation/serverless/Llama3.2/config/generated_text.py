import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_description(text, model_path="UICHEOL-HWANG/EcomGen-Llama3.2-3B", **kwargs):
    """
    상품명으로 설명 생성

    Args:
        text (str): EcomGen 모델이 생성한 텍스트
        model_path (str): 모델 경로
        **kwargs: 추가 생성 파라미터

    Returns:
        str: 생성된 설명
    """
    logging.info(f"모델 로드 중: {model_path}")

    # 모델과 토크나이저 로드
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        logging.info("모델 로드 완료")

    except Exception as e:
        logging.error(f"모델 로드 중 오류 발생: {e}")
        raise

    # 프롬프트 구성
    messages = [
        {"role": "user", "content": f"{text}"}
    ]

    logging.info(f"프롬프트 준비 완료")

    try:
        # 토크나이즈
        input_ids = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        terminators = [
            tokenizer.convert_tokens_to_ids("<|end_of_text|>"),
            tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        # 기본 생성 파라미터
        generation_params = {
            "eos_token_id": terminators,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature" : 0.6,
            "top_p" : 0.9
        }

        # 사용자 제공 파라미터로 기본값 덮어쓰기
        generation_params.update(kwargs)
        logging.info(f"생성 파라미터: {generation_params}")

        # 생성
        logging.info("텍스트 생성 중...")
        with torch.no_grad():
            output = model.generate(
                input_ids.to(model.device),
                **generation_params
            )

        # 디코딩
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

        # 응답 부분만 추출
        if "assistant" in generated_text.lower():
            response_parts = generated_text.split("assistant")
            if len(response_parts) > 1:
                generated_text = "assistant".join(response_parts[1:])

        logging.info(f"생성 완료: {len(generated_text)} 글자")

        return generated_text.strip()

    except Exception as e:
        logging.error(f"텍스트 생성 중 오류 발생: {e}")
        raise