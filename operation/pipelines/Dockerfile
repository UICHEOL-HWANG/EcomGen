FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 필요한 디렉토리만 복사
COPY evaluation_metrics.py .
COPY .env .
COPY storage/ ./storage/
COPY eval/ ./eval/

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 결과 저장용 디렉토리 생성
RUN mkdir -p /app/results /app/logs

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "print('healthy')" || exit 1

# 애플리케이션 실행
CMD ["python", "evaluation_metrics.py"]
