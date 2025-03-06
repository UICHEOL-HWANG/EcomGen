from langgraph.graph import StateGraph, END
from .generate_model import generate_description, create_description_pipeline
from .clean_text import clean_text

model_path = "UICHEOL-HWANG/EcomGen-0.0.1v"

# ✅ 1. 상품 설명 생성 노드
def generate_node(state):
    product_name = state["product_name"]  # ✅ 오타 수정

    pipe = create_description_pipeline(model_path)
    response = generate_description(pipe, product_name)

    state["generated_description"] = response
    return state

# ✅ 2. 상품 설명 정제 노드
def clean_node(state):
    description = state["generated_description"]

    cleaned_description = clean_text(description)
    state["cleaned_description"] = cleaned_description.strip()
    return state

# ✅ 3. LangGraph 워크플로우 설정 (dict를 사용)
workflow = StateGraph(dict)  # ✅ dict 기반 StateGraph 사용

# ✅ 4. 노드 추가
workflow.add_node("generate", generate_node)
workflow.add_node("clean", clean_node)

# ✅ 5. 순서 정의: 생성 → 정제 → 종료
workflow.set_entry_point("generate")  # ✅ entry_point 설정
workflow.add_edge("generate", "clean")  # ✅ 생성 후 정제로 이동
workflow.add_edge("clean", END)  # ✅ 정제 후 종료

# ✅ 6. LangGraph 실행 객체 생성
graph = workflow.compile()
