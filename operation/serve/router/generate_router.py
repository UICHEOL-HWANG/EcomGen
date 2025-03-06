from fastapi import APIRouter
from .workflow import graph
from dto.request import GenerateRequest

generate_router = APIRouter(
    prefix="/generate",
    tags=["Generate"],
    responses={404: {"description": "Not found"}},
)

@generate_router("/", response_model=dict)
async def generate_and_clean_description(request: GenerateRequest):
    state = {"product_name" : request.product_name}
    result = graph.invoke(state)

    return {
        "product_name": request.product_name,
        "generated_description": result["generated_description"],
        "cleaned_description": result["cleaned_description"]
    }
