# Project `EcomGen`

- 개요 : 이커머스 셀러들을 위한 `상품 설명 생성모델`, 더 이상 상품 설명을 위해 비싼 비용 들이지 않기 위해 만든 모델 


- 주요 현황 : 약 5개의 모델을 통해 성능 비교 

> 최종 선정 모델 
> 1. `Polyglot-1.3b`
> 2. `Gemma2-ko-2b-it`

### 최종모델 성능비교 

``` text

Polyglot-1.3b

=== 생성된 상품 설명 ===

상품명: 저당 초코바
상품 설명:   등 세계적인 건강식품 브랜드를 보유한 덴마크의 프리미엄 초콜릿, 덴마크 오덴세가 선보이는 저당 밀크코팅 공법의 초콜릿 바입니다. 덴마크 오덴세만의 차별
된 맛은 물론, 부드러운 식감과 풍부한 맛으로 누구나 부담 없이 즐길 수 있어요. 다크, 딸기&산딸기, 레몬&유자, 얼그레이 총 4종을 준비했는데요. 은은하게 스며든 새콤콤
콤한 과일 풍미에 우유나 커피 한 잔 곁들이면 더없이 행복할 거예요. 넉넉히 포장해 가족이나 주변 지인에게 나눠줄 선물로도 제격이랍니다.  1개(12g)의 제품 속에 2겹   의 화이트초콜릿이 샌드되어 있습니다. 입안 가득 느껴지는 달달함이 매력적이니 잊지 말고 하나씩 꺼내드세요.  
```


```text
Gemma2-2b-it 

Action1. 

상품명: 장조림
생성된 설명:
깔끔한 식탁을 완성하는 간식, 장조림이 참 매력적이죠. 갓 구운 돼지고기와 김치를 겹겹이 채어 끓인 탕에 넣은 장조림이에요. 식탁에 놓고 밥을 꺼내어 뚝뚝 밥을 풀어 넣, 계속 가득 채운 맛의 장조림을 드셔 보세요. 넉넉한 양이니, 한 번에 하나씩 꺼내 먹기 좋아요.

Action2. 

상품명: 저당 초코바
생성된 설명:
설탕이 적지 않은 간식이라 걱정을 가질 때, 그릇 하나만 있으면 충분하지요. 깨끗한 감귤의 맛을 풀어낸 꾸라의 저당 초코바를 선택해 보세요. 국내산 감귤로만 빚은 앙증 맞은 맛을 즐길 수 있답니다. 부드러운 초코바 사이에 감귤은 잘 붙어 있어 부담 없이 먹기 좋답니다.
```
    
### 결론 

- `Gemma2-2b-it`의 출력이 조금 더 깔끔하나, 문맥적으로 어색한 부분이 가장 크기에 Polyglot-1.3b를 사용하는 것으로 추진 
- 아이템 설명에 있어 어색한 부분은 대형 한국형 언어모델을 사용하여 교정하는 방법 사용 예정

----

# LLM과의 결합 

- `Polyglot-1.3b`과 `LG Exaone-3.5`의 결합으로 조금 더 매끄러우면서 창의적인 멘트 완성 


- 기존 `Polyglot-1.3b` 출력내용 
``` text
상품명: 저당 초코바

상품 설명: 🍫는 한 개만 먹어도 충분한 영양을 지니고 있지만, 다양하게 활용해보세요. 요거트에 넣어 유산균 발효를 시켜 드시거나, 
시리얼과 함께 즐기면 든든하고 깔끔한 맛을 느낄 수 있답니다. 또 딸기맛이나 블루베리맛 등 색다르게 선택하여 즐겨 보아도 좋아요. 저칼로리 제품이 부담스러울 
땐, 무설탕 🙅♀️ 초코 바를 추천해요. 

적당한 무게감으로 하나씩 먹기에도 알맞아 매일 간편히 즐길 수 있지요. 아이들 간식용이나 간단한 아침 식사로 👌 준비해도  
참 좋아할 거예요! https://bit.ly/3f4BtC2 상품 상세 정보를 확인해주세요. 📢 6개입 / 8,800원. 🎈 12개입 / 16,900원. https://link.coupang.com/re/SHARESDPTNE?pageKey=207030887138&vendorItemId=51887109869&isAddedCart= 글루텐 프리 무설탕 초콜릿바. https://smartstore.naver.com/marubely_lab/category/50002833?cp=1'
```

- `LG Exaone-3.5` 출력 내용
```text
**Supreme 저당 초코바** 🍫

### 수정된 상품 설명:
✨ **Supreme 저당 초코바** 🍫 – 세련된 맛과 균형 잡힌 영양으로 하루를 풍성하게 만드세요! 🥰 다양한 맛 라인업으로 취향에 맞춰 즐길 수 있는 유연성을 제공합니다. 신신
한 과일과의 조화로 아침 식사를 더욱 즐겁게 만들거나, 쫄깃한 식감과 깊은 초콜릿의 풍미를 느끼며 한 손에 잡히는 편리함을 경험해 보세요. 🍓🥩 **무설탕** 옵션은 건건
을 중시하는 여러분을 위한 선택입니다. 적당한 크기로 구성된 포장은 하루 한 개씩 간편하게 즐길 수 있게 설계되었으며, 바쁜 일상이나 가족과 함께하는 시간에 이상적   입니다. 특히 **글루텐 프리**로 알레르기를 걱정하지 않고 안전하게 즐길 수 있어 모든 연령대에게 적합합니다.

**제품 정보:**
- **📐 포장 크기**: 6개입 / 8,800원, 12개입 / 16,900원
- **📌 구매 링크**: [링크](https://link.coupang.com/re/SHARESDPTNE?pageKey=207030887138&vendorItemId=51887109869&isAddedCart=)
- **🌐 상세 페이지**: [상품 상세 페이지](https://smartstore.naver.com/marubely_lab/category/50002833?cp=1) 및 **글루텐 프리 인증** 확인

✨ **Supreme 저ㅈ당 초코바**로 건강하고 세련된 하루를 완성하세요! ✨
```

ㅋㅋ ㅁㅊ;; 성능 확실하고만