import torch
from diffusers import FluxPipeline
import io
import base64

class FluxGenerator:
    def __init__(self,
                 model_id="black-forest-labs/FLUX.1-schnell",
                 device="cuda",
                 dtype=torch.float16,
                 cpu_offload=False):
        self.pipe = FluxPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
        )

        if cpu_offload:
            self.pipe.enable_model_cpu_offload()

        self.pipe = self.pipe.to(device)

    def __call__(self,
                 prompt: str,
                 guidance_scale: float = 0.0,
                 num_inference_steps: int = 4,
                 max_sequence_length: int = 256,
                 seed: int = 0) -> str:
        generator = torch.Generator("cpu").manual_seed(seed)

        result = self.pipe(
            prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
            generator=generator
        ).images[0]

        buffer = io.BytesIO()
        result.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")