from mecab import MeCab
from collections import Counter
import re
from .category_piepelines import STOPWORDS

mecab = MeCab()

# 키워드 추출
def extract_keywords(text, top_n=10):
    if not text or not isinstance(text, str):
        return ""
    words = mecab.nouns(text)
    words = [w.strip().lower() for w in words if w not in STOPWORDS and len(w) > 1 and not w.isnumeric()]
    counter = Counter(words)
    top_keywords = [word for word, _ in counter.most_common(top_n)]
    return ", ".join(top_keywords).strip(", ")

# 제목에 있는 대괄호 제거
def clean_brackets(text):
    return re.sub(r"\[.*?\]", "", text).strip()

def remove_feature_keywords(text):
    keywords = [kw.strip() for kw in text.split(",")]
    filtered = [kw for kw in keywords if "컬리" not in kw]
    return ", ".join(filtered)

def fill_empty_words_with_short_desc(data):
    mask = data["words"].str.strip() == ""
    data.loc[mask, "words"] = data.loc[mask, "short_desc"]
    return data

def preprocess_name(data):
    data["name_cleaned"] = data["name"].astype(str).apply(clean_brackets)
    return data

def extract_and_clean_keywords(data):
    data["top_keywords"] = (
        data["words"].astype(str)
        .apply(extract_keywords)
        .apply(remove_feature_keywords)
    )
    return data

def feature_engineering(data):
    # 1. 결측치 제거
    data = data.loc[data["words"].notna() & data["short_desc"].notna()].reset_index(drop=True)

    # 2. 빈 words를 short_desc로 대체
    data = fill_empty_words_with_short_desc(data)

    # 3. name 전처리
    data = preprocess_name(data)

    # 4. 키워드 추출 및 필터링
    data = extract_and_clean_keywords(data)

    # 5. 최종 컬럼 선택
    main_columns = ['name_cleaned', 'main_category_name', 'sub_category_name', 'price', 'words', 'top_keywords']
    return data[main_columns].copy()