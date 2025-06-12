FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
# 기본 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# 작업 디렉토리 설정
WORKDIR /app
# Python 패키지 설치 (AI Agent 관련)
RUN pip install --no-cache-dir \
    runpod \
    transformers==4.51.3 \
    accelerate \
    tokenizers \
    langchain==0.3.10 \
    langchain-community==0.3.10 \
    langchain-huggingface==0.1.2 \
    langchain-core==0.3.21 \
    langgraph==0.2.57 \
    tavily-python \
    requests \
    httpx \
    numpy \
    pandas \
    python-dotenv \
    pydantic==2.10.3

# 프로젝트 파일 복사
COPY . .
# 환경변수 설정

ENV HF_HOME=/app/hf_cache
ENV PYTHONPATH=/app
ENV TOKENIZERS_PARALLELISM=false
ENV TRANSFORMERS_CACHE=/app/hf_cache
# 캐시 디렉토리 생성
RUN mkdir -p /app/hf_cache

# 컨테이너 시작 명령

CMD ["python", "main.py"]
