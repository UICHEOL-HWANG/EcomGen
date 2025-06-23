import requests
import json
import logging


class BaseCrawler:
    """
    모든 크롤러의 기본 클래스
    """

    def __init__(self, headers, cookies):
        self.headers = headers
        self.cookies = cookies

    def _make_request(self, url, params=None):
        """
        HTTP 요청을 보내고 응답을 JSON으로 반환하는 공통 메서드

        Args:
            url (str): 요청할 URL
            params (dict, optional): URL 파라미터

        Returns:
            dict: 응답 JSON 데이터 또는 오류시 빈 딕셔너리
        """
        try:
            response = requests.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                params=params
            )
            response.raise_for_status()
            return json.loads(response.text)
        except requests.RequestException as e:
            logging.error(f"HTTP 요청 실패: {e} - URL: {url}")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"JSON 파싱 오류: {e} - URL: {url}")
            return {}


class Crawl(BaseCrawler):
    """
    카테고리 정보를 가져오는 크롤러
    """

    def __init__(self, headers, cookie):
        super().__init__(headers, cookie)

    def update_headers(self, additional_headers):
        """
        헤더 정보 업데이트

        Args:
            additional_headers (dict): 추가할 헤더 정보

        Returns:
            dict: 업데이트된 헤더 정보
        """
        self.headers.update(additional_headers)
        return self.headers

    def fetch_data(self, url, category):
        """
        카테고리 데이터를 가져와 하위 카테고리 코드 목록을 반환

        Args:
            url (str): API URL
            category (str): 카테고리 코드

        Returns:
            list: 하위 카테고리 코드 목록
        """
        try:
            data = self._make_request(f"{url}/{category}")
            if not data:
                return []

            # 하위 카테고리 코드 추출
            return [i["code"] for i in data.get("data", {}).get("children", [])]

        except KeyError as e:
            logging.error(f"카테고리 데이터 구조 오류: {e}")
            return []


class ListCrawl(BaseCrawler):
    """
    제품 목록을 가져오는 크롤러
    """

    def __init__(self, header, cookie, params):
        super().__init__(header, cookie)
        self.params = params

    def fetch_list_data(self, url, category):
        """
        제품 목록 데이터를 가져옴

        Args:
            url (str): API URL
            category (str): 카테고리 코드

        Returns:
            list: 제품 목록 데이터
        """
        try:
            data = self._make_request(f"{url}{category}/products", self.params)
            if not data:
                return []

            return data.get("data", [])

        except KeyError as e:
            logging.error(f"제품 목록 데이터 구조 오류: {e}")
            return []