FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# 기본 패키지
RUN apt-get update && apt-get install -y \
    git wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    transformers \
    accelerate \
    requests \
    huggingface-hub \
    runpod

COPY . . /app/

ENV HF_HOME=/app/hf_cache

CMD ["python", "main.py"]