import os
from dotenv import load_dotenv

load_dotenv()

cookies = {
    'kdi': os.getenv('COOKIE_KDI'),
    '_fbp': os.getenv('COOKIE_FBP'),
    'ksi': os.getenv('COOKIE_KSI'),
    'krt': os.getenv('COOKIE_KRT'),
    '_clck': os.getenv('COOKIE_CLCK'),
    'cart_count': os.getenv('COOKIE_CART_COUNT'),
    '_clsk': os.getenv('COOKIE_CLSK'),
    'amp_65bebb': os.getenv('COOKIE_AMP_65BEBB'),
    'amplitudeBucket': os.getenv('COOKIE_AMPLITUDE_BUCKET'),
}

# 헤더 정보 (상수로 유지)
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'kurly-auth-dev': 'true',
    'origin': 'https://www.kurly.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

params = {
    'sort_type': '4',
    'page': '1',
    'per_page': '96',
    'filters': '',
}