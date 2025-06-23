# perplexity.py
import logging
from mecab import MeCab
from math import log
import random

logger = logging.getLogger(__name__)

def calculate_perplexity_cross_validation(text, ngram_order=2, smoothing=0.1):
    """
    크로스 밸리데이션 방식으로 perplexity 계산
    """
    if not text:
        return float('inf')
    
    try:
        # MeCab 초기화
        mecab = MeCab()
        
        # 텍스트 토큰화
        tokens = [token[0] for token in mecab.pos(text)]
        
        if len(tokens) < ngram_order * 2:  # 최소 토큰 수 체크
            logger.warning(f"텍스트가 너무 짧습니다: {len(tokens)} 토큰")
            return float('inf')
        
        # 랜덤 분할을 위한 시드 설정
        random.seed(42)
        
        # 70% 학습, 30% 테스트로 분할
        split_point = int(len(tokens) * 0.7)
        train_tokens = tokens[:split_point]
        test_tokens = tokens[split_point:]
        
        # 어휘 집합 구성
        vocabulary = set(tokens)
        vocab_size = len(vocabulary)
        
        # n-gram 및 컨텍스트 빈도 계산 (학습 데이터)
        ngrams = {}
        contexts = {}
        
        for i in range(len(train_tokens) - ngram_order + 1):
            ngram = tuple(train_tokens[i:i+ngram_order])
            context = tuple(train_tokens[i:i+ngram_order-1])
            
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
            contexts[context] = contexts.get(context, 0) + 1
        
        # 테스트 데이터에서 로그 확률 계산
        log_prob_sum = 0
        count = 0
        
        for i in range(len(test_tokens) - ngram_order + 1):
            ngram = tuple(test_tokens[i:i+ngram_order])
            context = tuple(test_tokens[i:i+ngram_order-1])
            
            # 컨텍스트와 n-gram 빈도
            context_count = contexts.get(context, 0)
            ngram_count = ngrams.get(ngram, 0)
            
            # 확률 계산 (스무딩 적용)
            if context_count > 0:
                prob = (ngram_count + smoothing) / (context_count + smoothing * vocab_size)
            else:
                # 처음 보는 컨텍스트의 경우 균등 분포 가정
                prob = 1.0 / vocab_size
            
            log_prob_sum += log(prob, 2)
            count += 1
        
        if count == 0:
            return float('inf')
        
        # 평균 로그 확률의 음수 지수
        perplexity = 2 ** (-log_prob_sum / count)
        return perplexity
    
    except Exception as e:
        logger.error(f"Perplexity 계산 오류: {str(e)}")
        return float('inf')

def calculate_keywords_perplexity(text, keywords, ngram_order=2, smoothing=0.1):
    """
    주어진 키워드를 포함하는지 여부와 함께 perplexity 계산
    """
    result = {
        "perplexity": calculate_perplexity_cross_validation(text, ngram_order, smoothing),
        "keywords_included": {},
        "keywords_count": 0
    }
    
    # 키워드 포함 여부 체크
    for keyword in keywords:
        included = keyword.lower() in text.lower()
        result["keywords_included"][keyword] = included
        if included:
            result["keywords_count"] += 1
    
    # 키워드 포함 비율
    result["keywords_ratio"] = result["keywords_count"] / len(keywords) if keywords else 0
    
    return result