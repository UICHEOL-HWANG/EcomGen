import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_description(product_name, model_path="UICHEOL-HWANG/EcomGen-0.0.1v", **kwargs):
    """
    상품명으로 설명 생성

    Args:
        product_name (str): 상품명
        model_path (str): 모델 경로
        **kwargs: 추가 생성 파라미터

    Returns:
        str: 생성된 설명
    """
    logging.info(f"모델 로드 중: {model_path}")

    # 올바른 from_pretrained 메서드 사용
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # 패딩 토큰 확인
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # GPU 사용 가능 시 모델 이동
    if torch.cuda.is_available():
        logging.info(f"모델이 GPU로 이동되었습니다: {model.device}")
    else:
        logging.info("GPU를 사용할 수 없어 CPU에서 실행됩니다")

    # 프롬프트 구성
    prompt = f"상품명: {product_name}\n상품 설명: "
    logging.info(f"프롬프트: {prompt}")

    # 기본 생성 파라미터
    generation_params = {
        "max_new_tokens": 512,
        "repetition_penalty": 1.15,
        "temperature": 1.0,
        "top_p": 0.9,
        "top_k": 40,
        "do_sample": True,
        "pad_token_id": tokenizer.eos_token_id  # 패딩 토큰 ID 설정
    }

    # 사용자 제공 파라미터로 기본값 덮어쓰기
    generation_params.update(kwargs)
    logging.info(f"생성 파라미터: {generation_params}")

    # 입력 토큰화
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # 텍스트 생성
    logging.info("텍스트 생성 중...")
    with torch.no_grad():
        output = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            **generation_params
        )

    # 생성된 텍스트 디코딩
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    logging.info(f"생성 완료: {len(generated_text)} 글자")

    return generated_text