import requests
import os

def translate_language(text: str)-> str:
    """

    :param text: 번역할 단어
    :return: 번역된 단어
    """

    if not text:
        return text

    params = {
        "auth_key": os.getenv("DEEPL_AUTH_KEY"),
        "text": text,
        "source_lang": "KO",
        "target_lang": "EN",
    }

    response = requests.post(os.getenv("DEEPL_URL"), data=params, verify=False)

    if response.status_code == 200:
        result_json = response.json()
        translated_text = result_json["translations"][0]["text"]
        return translated_text
    else:
        # 에러 시 원문 그대로 반환하거나, 원하는 처리를 해도 됨
        return text