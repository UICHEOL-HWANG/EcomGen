import os
import time
import requests
import hashlib
import hmac
import base64
import pandas as pd


class Signature:

    @staticmethod
    def generate(timestamp, method, uri, secret_key):
        message = "{}.{}.{}".format(timestamp, method, uri)
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
        return base64.b64encode(hash.digest()).decode()  # decode to str


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    signature = Signature.generate(timestamp, method, uri, secret_key)

    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }


def getresults(hintKeywords):

    BASE_URL = os.getenv("BASE_URL")
    API_KEY = os.getenv("API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    CUSTOMER_ID = os.getenv("CUSTOMER_ID")

    uri = '/keywordstool'
    method = 'GET'

    params = {
        'hintKeywords': hintKeywords,
        'showDetail': '1'
    }

    response = requests.get(BASE_URL + uri, params=params,
                            headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))

    response.raise_for_status()  # error 발생 시 예외 처리

    data = pd.DataFrame(response.json()['keywordList'])

    # 전처리 ">" 이거 제거 후에 숫자로 변환해주고, 월간 검색량 위주로 sort
    data["monthlyPcQcCnt"] = data["monthlyPcQcCnt"].apply(
        lambda x: int(str(x).replace("<", "").strip()) if str(x).replace("<", "").strip().isdigit() else 0
    )

    data = data.sort_values("monthlyPcQcCnt", ascending=False).reset_index(drop=True).iloc[:10][
        ["relKeyword", "monthlyPcQcCnt"]
    ]

    return data.to_dict(orient="records")