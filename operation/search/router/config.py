import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Tavily API 키
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "default_api_key")

# Ollama 모델 설정
OLLAMA_QWEN_CONFIG = {
    "model": "qwen2.5:3b",
    "api_type": "ollama",
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
}

OLLAMA_ECOMGEN_CONFIG = {
    "model": "EcomGen:0.0.1v",
    "api_type": "ollama",
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
}

# 기타 설정 필요시 추가 가능
