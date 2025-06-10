from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document

class WebSearch:
    def __init__(self, region="ko-kr", time="d", max_results=5):
        self.wrapper = TavilySearchAPIWrapper()
        self.search = TavilySearchResults(api_wrapper=self.wrapper, max_results=max_results)
    
    def get_relevant_documents(self, query: str):
        """웹 검색을 수행하고 Document 객체 리스트를 반환합니다."""
        try:
            results = self.search.run(query)
            
            # 결과를 Document 객체로 변환
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.get("content", ""),
                    metadata={
                        "source": result.get("url", ""),
                        "title": result.get("title", "")
                    }
                )
                documents.append(doc)
            
            return documents
        except Exception as e:
            print(f"웹 검색 중 오류 발생: {e}")
            return []

# 이전 코드와의 호환성을 위한 별칭
Web_search = WebSearch
