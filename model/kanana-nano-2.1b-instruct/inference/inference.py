import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = "../merge_kanana"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
).to("cuda")

tokenizer = AutoTokenizer.from_pretrained(model_path)

prompt = "주어진 상품명을 기반으로 매력적인 상품설명을 작성하세요.\n상품명: 장조림"
messages = [
    {"role": "system", "content": "당신은 상품명을 바탕으로 상세하고 매력적인 상품 설명을 생성하는 AI입니다."},
    {"role": "user", "content": prompt}
]

input_ids = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
).to("cuda")

_ = model.eval()
with torch.no_grad():
    output = model.generate(
        input_ids,
        max_new_tokens=512,
        do_sample=False,
    )

print(tokenizer.decode(output[0], skip_special_tokens=True))