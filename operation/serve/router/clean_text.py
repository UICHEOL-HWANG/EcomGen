from langchain_ollama import OllamaLLM

def clean_text(text):
    llm = OllamaLLM(model="Ecomgen:0.0.1v",
                    base_url="127.0.0.1:11434")

    prompt = f"""
    당신은 전문적인 상품 설명 에디터입니다. 다음 상품 설명을 읽고, 더 명확하고 매력적으로 다듬어주세요.

    원본 텍스트:
    {text}

    개선된 텍스트:
    """

    cleaned_text = llm.invoke(prompt)
    return cleaned_text
