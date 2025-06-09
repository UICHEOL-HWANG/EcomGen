from config.generated_image import FluxGenerator
import logging
import runpod

logging.basicConfig(level=logging.INFO)

generator = FluxGenerator()

def handler(event):
    try:
        prompt = event.get("input", {}).get("prompt")
        if not prompt:
            raise ValueError("Missing 'prompt' in event['input']")

        # 클래스 인스턴스를 함수처럼 호출!
        image_base64 = generator(
            prompt=prompt,
            num_inference_steps=6,
            seed=42
        )

        return {"image_base64": image_base64}

    except Exception as e:
        logging.exception("handler 오류 발생")
        return {
            "error": str(e),
            "hint": "event['input']에 'prompt' 키가 포함되어야 합니다. 예: {'input': {'prompt': 'A cat flying in space'}}"
        }


if __name__ == "__main__":
    runpod.serverless.start({"handler" : handler})