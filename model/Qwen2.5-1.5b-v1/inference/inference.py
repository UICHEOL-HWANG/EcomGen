import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    # 1. 파인튜닝된 모델과 토크나이저 불러오기
    model_path = "../merged_qwen"  # 병합된 모델 경로
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    # GPU 설정
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # 2. 인퍼런스용 프롬프트 구성 (브랜드 정보, 영양 성분 제외)
    system_message = (
        "당신은 고객이 관심을 가질 만한 매력적인 제품 설명을 생성하는 AI입니다. "
        "상품명에 맞는 상품 설명을 작성하세요. 단, 브랜드명, 출시일, 영양정보는 포함하지 마세요."
    )
    user_message = "소보로빵"  # 예시: 상품명을 입력하세요

    # ChatML 템플릿 사용
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    chatml_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,  # 문자열 형태로 생성
        add_generation_prompt=True  # 어시스턴트 응답 생성을 위한 프롬프트 토큰 추가
    )

    # 3. 프롬프트 토크나이징
    inputs = tokenizer(
        chatml_prompt,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    ).to(device)

    # 4. 모델로부터 응답 생성
    with torch.no_grad():
        with torch.autocast("cuda"):  # GPU 메모리 최적화
            outputs = model.generate(
                **inputs,
                max_new_tokens=120,  # ✅ 너무 길지 않게 제한 (200 → 120)
                num_beams=5,  # ✅ 빔 서치 유지
                do_sample=True,  # ✅ 샘플링 방식 유지
                top_p=0.9,  # ✅ 모델이 가장 가능성 높은 선택을 하도록 조정 (0.95 → 0.9)
                temperature=0.95,  # ✅ 랜덤성 줄이기 (1.3 → 0.95)
                no_repeat_ngram_size=3,  # ✅ 더 긴 반복 방지 (2 → 3)
                early_stopping=True,
                pad_token_id=tokenizer.eos_token_id  # ✅ padding 토큰 설정 (경고 메시지 제거)
            )

    # 5. 생성된 토큰 디코딩 (프롬프트 제외)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # "assistant" 이후의 텍스트만 가져오기
    if "assistant" in generated_text:
        assistant_output = generated_text.split("assistant", 1)[-1].strip()
    else:
        assistant_output = generated_text.strip()

    # 결과 출력
    print("✅ 생성된 설명:", assistant_output)


if __name__ == '__main__':
    main()
