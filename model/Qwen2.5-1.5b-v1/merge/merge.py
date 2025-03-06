import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def merge_adapter():
    # 1. Qwen 모델 및 토크나이저 로드
    model_name = "Qwen/Qwen2.5-1.5B"
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

    # 2. 학습한 Adapter (LoRA) 로드
    adapter_path = "../results"  # 학습된 어댑터 경로 (변경 필요)
    model = PeftModel.from_pretrained(model, adapter_path)
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)

    # 3. Adapter 병합
    model = model.merge_and_unload()  # 어댑터를 본 모d델과 병합
    print("✅ Adapter 병합 완료!")

    # 4. 병합된 모델 저장
    merged_model_path = "../merged_qwen"
    model.save_pretrained("./merged_qwen", safe_serialization=True)  # `safetensors`로 저장
    tokenizer.save_pretrained("./merged_qwen")
    print(f"✅ 병합된 모델이 {merged_model_path} 에 저장되었습니다.")

if __name__ == "__main__":
    merge_adapter()
