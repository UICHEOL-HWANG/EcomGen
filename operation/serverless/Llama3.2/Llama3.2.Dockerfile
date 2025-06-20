FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
# 기본 패키지
RUN apt-get update && apt-get install -y \
    git wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    transformers==4.51.3 \
    accelerate \
    requests \
    runpod \
    wandb

COPY . . /app/

ENV HF_HOME=/app/hf_cache

CMD ["python", "main.py"]