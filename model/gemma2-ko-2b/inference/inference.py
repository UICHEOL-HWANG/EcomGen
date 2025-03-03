import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)


class GemmaProductGenerator:
    def __init__(self, model_name="../results", quantize_4bit=True):
        """
        상품 설명 생성을 위한 Gemma-2B-IT 추론 클래스
        - 4비트 양자화 기본 적용 (검색 결과 [3][5] 반영)
        - 토크나이즈 자동화
        """
        # 양자화 설정
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=quantize_4bit,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        ) if quantize_4bit else None

        # 모델 및 토크나이저 로드 (검색 결과 [5] 참조)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            padding_side="right",
            add_eos_token=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto"
        )

        # 추론 파라미터 기본값
        self.default_params = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 50,
            "do_sample": True
        }

    def generate_description(self, product_name, **kwargs):
        """
        상품명 기반 설명 생성 (검색 결과 [4] 프롬프트 구조 적용)
        """
        # 프롬프트 템플릿 (검색 결과 [3] 채팅 형식)
        messages = [
            {"role": "user", "content": f"다음 상품명에 대한 매력적인 설명을 작성하세요:\n상품명: {product_name}"}
        ]

        # 입력 토크나이징 (검색 결과 [3] 방식)
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        # 추론 실행 (검색 결과 [5] 파라미터 조합)
        generate_params = {**self.default_params, **kwargs}
        outputs = self.model.generate(
            inputs,
            **generate_params
        )

        # 결과 디코딩 및 후처리
        response = self.tokenizer.decode(
            outputs[0][inputs.shape[1]:],
            skip_special_tokens=True
        )
        return response.strip()


# 사용 예시
if __name__ == "__main__":
    generator = GemmaProductGenerator()

    product = "저당 초코바"
    description = generator.generate_description(
        product,
        temperature=0.8,
        max_new_tokens=512
    )

    print(f"상품명: {product}")
    print(f"생성된 설명:\n{description}")
