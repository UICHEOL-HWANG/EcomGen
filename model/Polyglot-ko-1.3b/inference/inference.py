import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


def load_model(model_path):
    """ ✅ 학습된 모델과 토크나이저 로드 """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path).to("cuda")
    model.eval()
    return tokenizer, model


def generate_description(model, tokenizer, product_name, max_length=512):
    """ ✅ 상품명에 대한 설명을 생성하는 함수 """

    # ✅ EOS 토큰 설정
    eos_token = tokenizer.eos_token or tokenizer.pad_token or "<|endoftext|>"
    stop_token_id = tokenizer.eos_token_id or tokenizer.pad_token_id or \
                    tokenizer.encode(eos_token, add_special_tokens=False)[0]

    # ✅ 훈련된 데이터 패턴에 맞춘 프롬프트
    prompt = f"상품명: {product_name}\n상품 설명: "  # ✅ 훈련된 데이터 패턴 유지

    # ✅ 토큰화 및 입력값 변환 (불필요한 token_type_ids 제거)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    inputs.pop("token_type_ids", None)

    # ✅ 생성 실행
    output = model.generate(
        **inputs,
        max_new_tokens=max_length,
        repetition_penalty=1.15,  # ✅ 반복 방지
        temperature=1.0,  # ✅ 창의성 조절
        top_p=0.9,  # ✅ 다양한 응답 생성
        top_k=40,  # ✅ 확률적으로 상위 50개 단어 중 선택
        do_sample=True,  # ✅ 샘플링 활성화 (중요!)
        pad_token_id=stop_token_id,  # ✅ 패딩 시 EOS 토큰 적용
        eos_token_id=stop_token_id,  # ✅ EOS 토큰 적용
    )

    # ✅ 결과 디코딩
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    return generated_text


if __name__ == "__main__":
    """ ✅ 메인 실행 함수 """
    model_path = "../merged_polyglot"  # ✅ 학습된 모델 경로
    tokenizer, model = load_model(model_path)

    # ✅ 테스트할 상품명 입력
    product_name = "저당 초코바"
    description = generate_description(model, tokenizer, product_name)

    print("\n=== 생성된 상품 설명 ===\n")
    print(description)
