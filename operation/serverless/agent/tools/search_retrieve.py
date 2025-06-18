from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
import logging

class WebSearch:
    def __init__(self, region="ko-kr", time="d", max_results=3):
        self.wrapper = TavilySearchAPIWrapper()
        self.search = TavilySearchResults(api_wrapper=self.wrapper, max_results=max_results)

    def get_relevant_documents(self, query: str):
        """웹 검색을 수행하고 Document 객체 리스트를 반환합니다."""
        try:
            logging.info(f"🔍 웹 검색 중: {query}")
            results = self.search.run(query)

            # 결과를 Document 객체로 변환
            documents = []
            for i, result in enumerate(results):
                doc = Document(
                    page_content=result.get("content", "")[:500] + "...",  # 길이 제한
                    metadata={
                        "source": result.get("url", ""),
                        "title": result.get("title", "")
                    }
                )
                documents.append(doc)
                logging.info(f"검색결과 {i+1}: {result.get('title', 'No title')}")

            return documents
        except Exception as e:
            logging.info(f"❌ 웹 검색 중 오류 발생: {e}")
            return []


# 이전 코드와의 호환성을 위한 별칭
Web_search = WebSearch
