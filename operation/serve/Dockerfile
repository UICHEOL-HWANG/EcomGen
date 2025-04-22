FROM python:3.10-slim

ENV VLLM_TARGET_DEVICE=cpu

RUN apt-get update && \
    apt-get install -y git gcc-12 g++-12 libnuma-dev curl && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 10 \
        --slave /usr/bin/g++ g++ /usr/bin/g++-12

RUN pip install --upgrade pip && \
    pip install wheel packaging ninja "setuptools>=49.4.0" numpy

# vLLM 소스 클론
RUN git clone https://github.com/vllm-project/vllm.git /vllm
WORKDIR /vllm

# CPU용 의존성 설치
RUN pip install -r requirements-cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 직접 설치
RUN python setup.py install

# 앱 복사 후 실행
WORKDIR /app
COPY . /app
CMD ["python", "main.py"]
