# ShopLingo

### **EcomGen 언어모델을 활용한 이커머스 상품 설명 자동 생성 플랫폼**


> ShopLingo는 이커머스 셀러들이 상품 설명 작성에 소요되는 시간과 비용을 절약할 수 있도록 개발된 AI 기반 상품 설명 자동 생성 서비스입니다. 

> 자체 개발한 EcomGen 언어모델을 통해 고품질의 한국어 상품 설명을 생성합니다.


## 🏗️ 프로젝트 구조

```
ShopLingo/
├── model/              # EcomGen 언어모델
│   ├── config/         # 모델 설정 파일
│   ├── data/           # 학습 데이터셋
│   └── main.py         # 모델 실행 스크립트
├── operation/          # 운영 환경
│   ├── backend/        # FastAPI 백엔드 서버
│   ├── frontend/       # Vue.js 프론트엔드
│   ├── lambda/         # AWS Lambda 함수
│   ├── pipelines/      # 성능평가 파이프라인
│   ├── proxy/          # 프록시 설정
│   └── serverless/     # 서버리스 배포 설정
└── scraping/           # 데이터 수집 모듈
    ├── config/         # 크롤링 설정
    ├── data/           # 수집된 데이터
    ├── storage/        # 저장소 관리
    └── main.py         # 크롤링 실행 스크립트
```

## 🤖 EcomGen 모델

### 모델 선정 과정
초기에는 5개 이상의 모델(Polyglot-1.3b, Gemma2-ko-2b-it 등)을 비교 실험했으나, 단순히 상품명만으로는 카테고리 정보 부족으로 인한 정확도 저하가 발생했습니다.

### 최종 선정 모델
- **Bllossom/llama-3.2-Korean-Bllossom-3B**
- **google/gemma-3-4b-it**

### 데이터셋 개선
- GPT-nano4.1을 활용한 배치 API로 9,000개 → 20,000개로 데이터 증폭
- 5가지 입력 요소로 구성: 상품명, 카테고리, 가격, 핵심 키워드, 작성 톤
- MeCab 형태소 분석기를 통한 자동 키워드 추출 및 재정렬

## 🛠️ 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **PostgreSQL**: 주 데이터베이스
- **SQLAlchemy**: ORM
- **Alembic**: 데이터베이스 마이그레이션
- **AWS S3**: 파일 저장소

### Frontend
- **Vue.js 3**: 프론트엔드 프레임워크
- **Vite**: 빌드 도구
- **Tailwind CSS**: 스타일링
- **Pinia**: 상태 관리
- **Axios**: HTTP 클라이언트

### AI/ML
- **Transformers**: 모델 라이브러리
- **MeCab**: 한국어 형태소 분석
- **OpenAI API**: 데이터 증강
- **PyTorch**: 딥러닝 프레임워크

### Infrastructure
- **AWS Lambda**: 서버리스 컴퓨팅
- **AWS S3**: 정적 파일 호스팅 및 저장
- **Docker**: 컨테이너화
- **PostgreSQL**: 데이터베이스


## 👨‍💻 개발자

**UICHEOL-HWANG**
- Email: cheorish.hw@gmail.com
- GitHub: [@UICHEOL-HWANG](https://github.com/UICHEOL-HWANG)

## 🙏 감사의 말

- [Bllossom](https://huggingface.co/Bllossom) - 한국어 언어모델 제공
- [Google](https://huggingface.co/google) - Gemma 모델 제공
- 오픈소스 커뮤니티의 모든 기여자들

---

