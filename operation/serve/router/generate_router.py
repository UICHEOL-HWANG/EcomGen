from fastapi import APIRouter
from .generate_model import generate_description, create_description_pipeline
from .clean_text import clean_text
from dto.request import GenerateRequest

generate_router = APIRouter(
    prefix="/generate",
    tags=["Generate"],
    responses={404: {"description": "Not found"}},
)


@generate_router.post("/", response_model=dict)
async def generate_and_clean_description(request: GenerateRequest):
    product_name = request.product_name

    # 1. ✅ 생성 파이프라인 로드
    pipe = create_description_pipeline("UICHEOL-HWANG/EcomGen-0.0.1v")

    # 2. ✅ 상품 설명 생성
    raw_description = generate_description(pipe, product_name)

    # 3. ✅ 생성된 설명 다듬기
    cleaned_description = clean_text(raw_description)

    # 4. ✅ 결과 반환
    return {
        "product_name": product_name,
        "generated_description": raw_description,
        "cleaned_description": cleaned_description
    }
