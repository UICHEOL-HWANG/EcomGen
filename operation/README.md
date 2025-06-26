# EcomGen Operation

이커머스 상품 설명 자동 생성 AI 서비스 **EcomGen**의 운영 환경 및 인프라 구성을 관리하는 디렉토리입니다.

## 📁 디렉토리 구조

```
operation/
├── backend/           # FastAPI 백엔드 서버
├── frontend/          # Vue.js 프론트엔드 애플리케이션
├── lambda/           # AWS Lambda 서버리스 함수들
├── pipelines/        # 데이터 파이프라인 및 모델 평가
├── proxy/           # Nginx 리버스 프록시 설정
├── serverless/      # 서버리스 AI 모델 서빙
└── .env            # 환경 변수 설정
```

## 🚀 주요 컴포넌트

### 1. Backend (`/backend`)
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL (SQLAlchemy ORM)
- **인증**: JWT 토큰 기반 인증
- **주요 기능**:
  - 사용자 관리 및 인증
  - 상품 설명 생성 API
  - 상품 검색 및 키워드 분석
  - 사용량 리포트 생성

**실행 방법**:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend (`/frontend`)
- **프레임워크**: Vue.js 3 + Vite
- **상태 관리**: Pinia
- **스타일링**: Tailwind CSS
- **배포**: AWS S3 + CloudFront

**실행 방법**:
```bash
cd frontend
npm install
npm run dev
```

**배포**:
```bash
npm run deploy
```

### 3. Lambda Functions (`/lambda`)
서버리스 함수들로 구성된 마이크로서비스 아키텍처:

#### Text Generation (`/lambda/text`)
- 상품 설명 텍스트 생성
- AI 모델 추론 처리

#### Keyword Extraction (`/lambda/keyword`)
- MeCab 형태소 분석
- 키워드 추출 및 최적화

#### Image Processing (`/lambda/image`)
- 상품 이미지 분석
- 이미지 기반 설명 생성

**배포**:
```bash
cd lambda/text
serverless deploy
```

### 4. Pipelines (`/pipelines`)
데이터 처리 및 모델 학습/평가 파이프라인:

- **Data Cleansing**: 학습 데이터 전처리
- **Model Evaluation**: 모델 성능 평가
- **Monitoring**: W&B를 통한 실험 추적

**실행**:
```bash
cd pipelines
python evaluation_metrics.py
```

### 5. Proxy (`/proxy`)
- **Nginx** 리버스 프록시
- SSL 터미네이션
- 로드 밸런싱
- CORS 및 보안 헤더 설정

### 6. Serverless AI Models (`/serverless`)
컨테이너 기반 AI 모델 서빙:

- **Llama3.2**: 한국어 텍스트 생성 모델
- **Gemma-3**: 다국어 텍스트 생성 모델
- **FLUX.1**: 이미지 생성 모델
- **Agent**: 멀티모달 AI 에이전트

## 🛠 기술 스택

### Backend
- **API**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT + bcrypt
- **Validation**: Pydantic
- **Migration**: Alembic

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **Styling**: Tailwind CSS
- **Charts**: Chart.js

### Infrastructure
- **Cloud**: AWS (Lambda, S3, CloudFront, RDS)
- **Container**: Docker + Docker Compose
- **Proxy**: Nginx
- **Monitoring**: W&B, CloudWatch
- **CI/CD**: Serverless Framework

### AI/ML
- **Models**: Llama3.2, Gemma-3, FLUX.1
- **NLP**: MeCab (한국어 형태소 분석)
- **Framework**: PyTorch, Transformers
- **Deployment**: AWS Lambda + Docker

## 🔧 환경 설정

### 필수 환경 변수
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-northeast-2

# Model Endpoints
LLAMA_ENDPOINT=your_lambda_endpoint
GEMMA_ENDPOINT=your_lambda_endpoint
```

## 🚀 배포 가이드

### 1. Backend 배포
```bash
cd backend
docker build -f backend.Dockerfile -t ecomgen-backend .
docker-compose -f back.docker-compose.yaml up -d
```

### 2. Frontend 배포
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://shop-lingo.store --delete
```

### 3. Lambda 함수 배포
```bash
cd lambda/text
serverless deploy

cd ../keyword
serverless deploy
```

### 4. AI 모델 배포
```bash
cd serverless/Llama3.2
docker build -f Llama3.2.Dockerfile -t ecomgen-llama .
# ECR 푸시 및 Lambda 업데이트
```

## 📊 모니터링

- **Application Logs**: FastAPI 로깅
- **Performance**: W&B 실험 추적
- **Infrastructure**: AWS CloudWatch
- **Error Tracking**: 애플리케이션 레벨 로깅

## 🔒 보안

- **HTTPS**: SSL/TLS 암호화
- **CORS**: 도메인 기반 접근 제어
- **CSP**: Content Security Policy 적용
- **JWT**: 토큰 기반 인증
- **Input Validation**: Pydantic 스키마 검증

## 📈 확장성

- **수평 확장**: Lambda 함수 자동 스케일링
- **캐싱**: 모델 추론 결과 캐싱
- **CDN**: CloudFront를 통한 전역 배포
- **Database**: 읽기 복제본 지원

## 🛠 개발 환경 구성

### 전체 스택 로컬 실행
```bash
# Backend
cd backend
docker-compose -f back.docker-compose.yaml up -d

# Frontend
cd frontend
npm run dev

# Proxy (선택사항)
cd proxy
docker-compose -f proxy.server.docker-compose.yaml up -d
```

