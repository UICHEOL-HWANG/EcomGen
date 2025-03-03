from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

def create_description_pipeline(model_path):
    """ ✅ 상품 설명 생성을 위한 파이프라인 생성 """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    # 파이프라인 생성
    description_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        repetition_penalty=1.15,
        temperature=1.0,
        top_p=0.9,
        top_k=40,
        do_sample=True
    )

    return description_pipeline

def generate_description(pipeline, product_name):
    """ ✅ 파이프라인을 사용하여 상품 설명 생성 """
    prompt = f"상품명: {product_name}\n상품 설명: "
    result = pipeline(prompt, max_new_tokens=512)  # max_length 대신 max_new_tokens 사용
    print(result)
    return result[0]['generated_text']
