import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Gemma-3 모델인 경우 TorchDynamo 비활성화
if "gemma" in model_path.lower():
    os.environ["TORCHDYNAMO_DISABLE"] = "1"


def generate_description(product_name, model_path="UICHEOL-HWANG/EcomGen-Gemma3-4B", **kwargs):
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

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    # 패딩 토큰 확인
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 프롬프트 구성
    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": product_name}]
    }]


    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )

    logging.info(f"프롬프트: {messages}")

    # 기본 생성 파라미터
    generation_params = {
        "max_new_tokens": 512,
        "repetition_penalty": 1.15,
        "temperature": 1.0,
        "top_p": 0.9,
        "top_k": 40,
        "do_sample": True,
        "pad_token_id": tokenizer.eos_token_id
    }

    generation_params.update(kwargs)
    logging.info(f"생성 파라미터: {generation_params}")

    # 입력 토큰화
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

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