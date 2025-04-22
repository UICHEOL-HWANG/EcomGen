from fastapi import APIRouter, Request
from vllm import SamplingParams
from dto.request import QueryRequest

generate_router = APIRouter(prefix="/generate", tags=["Generate"])

@generate_router.post("/", response_model=dict)
async def generate_and_clean_description(request: Request, payload: QueryRequest):
    product_name = payload.product_name
    llm = request.app.state.llm


    prompt = f"상품명: {product_name}"

    sampling_params = SamplingParams(
        temperature=1.0,
        top_p=0.9,
        top_k=40,
        repetition_penalty=1.15,
        max_tokens=512,
        seed=42
    )

    request_id = f"gen-{product_name[:10]}"
    results_generator = llm.generate(prompt=prompt, sampling_params=sampling_params, request_id=request_id)

    raw_description = ""
    async for output in results_generator:
        raw_description = output.outputs[0].text
        if output.finished:
            break

    return {
        "product_name": product_name,
        "generated_description": raw_description,
    }

