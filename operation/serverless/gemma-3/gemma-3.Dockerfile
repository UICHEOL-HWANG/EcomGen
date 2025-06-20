FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    git wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# transformers를 명시된 안전 버전으로 고정
RUN pip install --no-cache-dir \
    transformers \
    accelerate \
    requests \
    runpod

COPY . . /app/

# Hugging Face 모델 캐시 위치 설정
ENV HF_HOME=/app/hf_cache

ENV TORCHDYNAMO_DISABLE=1

CMD ["python", "main.py"]