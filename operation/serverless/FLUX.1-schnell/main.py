from config.generated_image import FluxGenerator
import logging
import runpod
import wandb
import time
import os
import base64
from datetime import datetime
import io
from PIL import Image

logging.basicConfig(level=logging.INFO)

generator = FluxGenerator()

# Wandb 설정
WANDB_PROJECT = os.getenv("WANDB_PROJECT", "ecomgen-image-generation")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")

def init_wandb(user_id=None):
    """Wandb 초기화"""
    if WANDB_API_KEY:
        try:
            timestamp = datetime.now().strftime("%m%d_%H%M")
            run_name = f"user{user_id or 'unknown'}_{timestamp}_image"
            
            wandb.init(
                project=WANDB_PROJECT,
                job_type="image-generation",
                name=run_name,
                tags=[f"user_{user_id}" if user_id else "no_user", "flux-image"],
                mode="online" if WANDB_API_KEY else "disabled"
            )
            return True
        except Exception as e:
            logging.warning(f"Wandb 초기화 실패: {e}")
            return False
    return False

def log_to_wandb(input_data, output_data, metrics):
    """Wandb에 로깅"""
    try:
        # Base64를 PIL Image로 변환
        image_data = base64.b64decode(output_data["image_base64"])
        image = Image.open(io.BytesIO(image_data))
        
        wandb.log({
            # Input 메트릭
            "input/prompt": input_data["prompt"],
            "input/prompt_length": len(input_data["prompt"]),
            "input/korean_text": input_data.get("korean_text", ""),
            "input/user_id": input_data.get("user_id"),
            
            # Output 메트릭
            "output/image_width": image.width,
            "output/image_height": image.height,
            "output/image_size_kb": len(output_data["image_base64"]) * 0.75 / 1024,  # base64 크기 추정
            
            # Performance 메트릭
            "performance/inference_time_seconds": metrics["inference_time"],
            "performance/num_inference_steps": metrics.get("num_inference_steps", 6),
            "performance/seed": metrics.get("seed", 42),
            
            # 실제 이미지 저장
            "generated_image": wandb.Image(
                image, 
                caption=f"Prompt: {input_data['prompt'][:100]}{'...' if len(input_data['prompt']) > 100 else ''}"
            ),
            
            "timestamp": datetime.now().timestamp()
        })
        
        logging.info("Wandb 로깅 완료")
    except Exception as e:
        logging.error(f"Wandb 로깅 실패: {e}")

def handler(event):
    wandb_enabled = False
    try:
        input_data = event.get("input", {})
        prompt = input_data.get("prompt")
        user_id = input_data.get("user_id")
        korean_text = input_data.get("korean_text", "")
        
        if not prompt:
            raise ValueError("Missing 'prompt' in event['input']")

        # Wandb 초기화
        wandb_enabled = init_wandb(user_id)
        
        # 성능 측정 시작
        start_time = time.time()
        
        # 클래스 인스턴스를 함수처럼 호출!
        image_base64 = generator(
            prompt=prompt,
            num_inference_steps=6,
            seed=42
        )
        
        # 성능 측정 종료
        inference_time = time.time() - start_time
        
        # 결과 데이터
        output_data = {"image_base64": image_base64}
        
        # Wandb 로깅
        if wandb_enabled:
            metrics = {
                "inference_time": inference_time,
                "num_inference_steps": 6,
                "seed": 42
            }
            log_to_wandb(input_data, output_data, metrics)
            wandb.finish()
        
        logging.info(f"이미지 생성 완료 - {inference_time:.2f}초")
        return output_data

    except Exception as e:
        logging.exception("handler 오류 발생")
        
        # 오류도 Wandb에 로깅
        if wandb_enabled:
            wandb.log({"error": str(e), "status": "failed"})
            wandb.finish()
            
        return {
            "error": str(e),
            "hint": "event['input']에 'prompt' 키가 포함되어야 합니다. 예: {'input': {'prompt': 'A cat flying in space', 'user_id': 123, 'korean_text': '고양이'}}"
        }


if __name__ == "__main__":
    runpod.serverless.start({"handler" : handler})