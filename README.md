# ShopLingo

### **`EcomGen` 언어모델을 활용한 이커머스 상품 설명 자동 생성 플랫폼**


> ShopLingo는 이커머스 셀러들이 상품 설명 작성에 소요되는 시간과 비용을 절약할 수 있도록 개발된 AI 기반 상품 설명 자동 생성 서비스입니다. 

> 자체 개발한 EcomGen 언어모델을 통해 고품질의 한국어 상품 설명을 생성합니다.

<img width="392" alt="image" src="https://github.com/user-attachments/assets/9973cff5-54d2-44c9-a3df-7132aa79d9bd" />

-------------

**🚀 [ShopLingo 서비스 체험하기](https://shop-lingo.store)**
- 본 서비스의 UI는 별도의 웹 서버 없이, AWS S3를 활용한 정적 호슽이 방식으로 배포되었습니다. 

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

## Project Abstract 

- 프로젝트 개요
    - 본 프로젝트는 B2B 사업자들을 위한 AI 기반 상품 콘텐츠를 자동생성 해주는 플랫폼입니다(단일 텍스트 입력 → 이미지,텍스트 생성)
- 프로젝트 목표
    - 사용자는 본인이 원하는 상품명을 입력하면, 그에 따른 상품설명, 상품사진의 초안을 작성해주는 서비스 구현

### 배경 

![image](https://github.com/user-attachments/assets/7d52d3dc-1ed2-4936-91f5-4811584fffbe)

- 2023년 말, ChatGPT와 같은 각종 AI를 활용한 컨텐츠 자동 생성 플랫폼이 블로거들과 부업러들 그리고 마케터들 사이에서 혁신을 일으키고 있었습니다.키워드 한개만 입력하면 블로그 제목부터 본문까지 자동으로 생성해주는 서비스들이 쏟아져 나왔고,부업러나 개인 브랜드를 운영하는 자영업자 분들에게는 필수 도구가 되어 가고 있습니다.


![image](https://github.com/user-attachments/assets/736f8acf-6891-4ddf-a8b9-67ae9b00a6a0)

- 많은 셀러들이 AI를 활용해 구매 욕구를 자극하는 상품 콘텐츠를 생성하고 있지만, 후처리 없이 곧바로 활용하기에는 사용자 경험 측면에서 한계가 있었습니다. 이에 따라, 최소한의 수정만으로 즉시 사용할 수 있는 상품 콘텐츠 생성 모델, `EcomGen`을 기획하게 되었습니다.


### 시장 분석 (Market Overview)

![image](https://github.com/user-attachments/assets/cacfe3b1-041f-467e-a82c-3ac4d4f01117)



- TAM (Total Addressable Market) - 글로벌 이커머스 시장
	- 글로벌 AI 기반 상품 콘텐츠 생성 시장은 $16.9B → $109.4B까지 성장이 예상됩니다. (2024년도 기준)

- SAM (Serviceable Available Market) - 한국 이커머스 시장
     - 한국 전체 이커머스 시장 규모: ₩229조
	 - B2C 이커머스 시장 규모: ₩149조

- SOM (Serviceable Obtainable Market) - 실제 타겟 시장
     - 국내 주요 이커머스 플랫폼 (네이버 스마트스토어, 쿠팡, 11번가 등) 기준 약 95만 명의 셀러가 활동 중이며, 이 중 1%인 9,500명을 초기 타겟 고객(소규모 셀러)으로 설정하였습니다.

## UseCase

https://github.com/user-attachments/assets/084b4f0c-3576-4a07-ac73-9b1de4ace0d1

> 1. 웹서버 접속, → 로그인 창 안내
> 2. 접속 후 메인페이지에서 다른 사람이 생성했던 내역들 및 에이전트 통한 리포트 생성 페이지
> 3. 하단 맨 왼쪽 AI생성 클릭
> 4. 본인이 원하는 옵션에 맞게 설정
> 5. 생성 후 최소 4분, 빠르면 1분이내로 생성가능(서버리스 특성상 콜드스타트 고려)
> 6. 마이페이지를 통해 내가 만든 상품 및 내가 저장한 리포트 확인 가능





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



## 👨‍💻 개발자

**UICHEOL-HWANG**
- Email: cheorish.hw@gmail.com
- GitHub: [@UICHEOL-HWANG](https://github.com/UICHEOL-HWANG)

## 🙏 감사의 말

- [Bllossom](https://huggingface.co/Bllossom) - 한국어 언어모델 제공
- [Google](https://huggingface.co/google) - Gemma 모델 제공
- 오픈소스 커뮤니티의 모든 기여자들

---

