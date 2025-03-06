import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def merge_adapter():
    # 1. 베이스 모델 및 토크나이저 로드
    model_name = "EleutherAI/polyglot-ko-1.3b"
    model = AutoModelForCausalLM.from_pretrained(model_name)


    # 2. 학습된 Adapter (LoRA) 로드
    adapter_path = "../results"  # 어댑터 모델이 저장된 경로
    model = PeftModel.from_pretrained(model, adapter_path)
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)
    # 3. Adapter 병합
    model = model.merge_and_unload()  # 어댑터 가중치를 본 모델과 병합
    print("✅ Adapter 병합 완료!")

    # 4. 병합된 모델 저장 (추론 시 어댑터 없이 단일 모델 사용 가능)
    merged_model_path = "../merged_polyglot"
    model.save_pretrained(merged_model_path)
    tokenizer.save_pretrained(merged_model_path)
    print(f"✅ 병합된 모델이 {merged_model_path} 에 저장되었습니다.")

if __name__ == "__main__":
    merge_adapter()
