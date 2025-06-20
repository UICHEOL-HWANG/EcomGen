import logging
import traceback
from config.generated_text import generate_description
import runpod
import wandb
import time
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Wandb 설정
WANDB_PROJECT = os.getenv("WANDB_PROJECT", "ecomgen-text-generation")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")

def init_wandb(user_id=None):
    """Wandb 초기화"""
    if WANDB_API_KEY:
        try:
            timestamp = datetime.now().strftime("%m%d_%H%M")
            run_name = f"user{user_id or 'unknown'}_{timestamp}_text"
            
            wandb.init(
                project=WANDB_PROJECT,
                job_type="text-generation",
                name=run_name,
                tags=[f"user_{user_id}" if user_id else "no_user", "llama-text"],
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
        wandb.log({
            # Input 메트릭
            "input/text": input_data["prompt"],
            "input/text_length": len(input_data["prompt"]),
            "input/user_id": input_data.get("user_id"),
            "input/temperature": input_data.get("generation_params", {}).get("temperature", 0.8),
            
            # Output 메트릭  
            "output/generated_text_length": len(output_data["description"]),
            "output/word_count": len(output_data["description"].split()),
            
            # Performance 메트릭
            "performance/inference_time_seconds": metrics["inference_time"],
            "performance/tokens_per_second": metrics.get("tokens_per_second", 0),
            
            "timestamp": datetime.now().timestamp()
        })
        
        # 상세 테이블
        table = wandb.Table(
            columns=["input_text", "generated_text", "inference_time", "word_count"],
            data=[[
                input_data["prompt"] + "..." if len(input_data["prompt"]) > 100 else input_data["prompt"],  # ✅ prompt 사용
                output_data["description"] + "..." if len(output_data["description"]) > 200 else output_data["description"],
                metrics["inference_time"],
                len(output_data["description"].split())
            ]]
        )
        wandb.log({"text_generation_details": table})
        
        logging.info("Wandb 로깅 완료")
    except Exception as e:
        logging.error(f"Wandb 로깅 실패: {e}")


def handler(event):
    """
    Runpod Serverless 핸들러 - 텍스트 재생성

    Args:
        event: 요청 이벤트
            {
                "input": {
                    "prompt": "재생성할 텍스트",
                    "user_id": 123,
                    "korean_text": "한국어 텍스트",
                    "generation_params": {
                        "temperature": 0.8,
                        ...
                    }
                }
            }

    Returns:
        dict: 생성된 설명
            {
                "description": "재생성된 텍스트"
            }
    """
    wandb_enabled = False
    try:
        # 입력 데이터 가져오기
        input_data = event.get("input", {})
        user_id = input_data.get("user_id")

        if "prompt" not in input_data:
            return {
                "error": "입력에 'prompt' 필드가 필요합니다"
            }

        # Wandb 초기화
        wandb_enabled = init_wandb(user_id)
        

        prompt_text = input_data["prompt"]
        korean_text = input_data.get("korean_text", "")
        generation_params = input_data.get("generation_params", {})

        logging.info(f"텍스트 재생성 중 (길이: {len(prompt_text)}, 사용자: {user_id})")

        # 성능 측정 시작
        start_time = time.time()
        
        # 설명 생성
        generated_text = generate_description(prompt_text, **generation_params)
        
        # 성능 측정 종료
        inference_time = time.time() - start_time
        
        # 결과 데이터
        output_data = {
            "description": generated_text
        }
        
        # Wandb 로깅
        if wandb_enabled:
            metrics = {
                "inference_time": inference_time,
                "tokens_per_second": len(generated_text.split()) / inference_time if inference_time > 0 else 0
            }
            log_to_wandb(input_data, output_data, metrics)
            wandb.finish()

        logging.info(f"텍스트 생성 완료 - {inference_time:.2f}초")
        return output_data

    except Exception as e:
        logging.error(f"핸들러 실행 중 오류 발생: {str(e)}")
        logging.error(traceback.format_exc())
        
        # 오류도 Wandb에 로깅
        if wandb_enabled:
            wandb.log({"error": str(e), "status": "failed"})
            wandb.finish()

        # 오류 결과 반환
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    runpod.serverless.start({"handler" : handler})