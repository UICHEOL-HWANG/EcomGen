FROM python:3.9-slim-buster

WORKDIR /generate


COPY . .

# ✅ 필요한 패키지 미리 설치 (시스템 패키지 포함)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "main.py"]