from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams

import torch

def create_async_llm_engine(
    model_path: str,
    gpu_util: float = 0.95,
    tp_size: int = 1,
    force_cpu: bool = False
) -> AsyncLLMEngine:
    is_cpu = force_cpu or not torch.cuda.is_available()
    dtype = "float32" if is_cpu else "float16"

    engine_args = AsyncEngineArgs(
        model=model_path,
        gpu_memory_utilization=gpu_util if not is_cpu else 0,
        tensor_parallel_size=tp_size if not is_cpu else 1,
        dtype=dtype,
    )
    return AsyncLLMEngine.from_engine_args(engine_args)

