from prompt.prompts import PromptChain
from state.agent_state import AgentState
from tools.search_retrieve import WebSearch
from langchain.schema import Document

def simple_search_node(state: AgentState, llm) -> AgentState:
    """
    웹 검색을 수행하고 LLM으로 답변을 생성하는 노드
    """
    try:
        query = state["input"]
        
        # 웹 검색 수행
        search = WebSearch()
        docs = search.get_relevant_documents(query)
        web_results = "\n\n".join([doc.page_content for doc in docs])
        
        # 프롬프트에 웹 검색 결과와 질문 전달
        result = llm.invoke({
            "question": query,
            "web_results": web_results
        })
        
        return {
            **state,
            "web_results": web_results,
            "result": result
        }
        
    except Exception as e:
        print(f"search_node에서 오류 발생: {e}")
        return {
            **state,
            "web_results": "",
            "result": f"검색 중 오류가 발생했습니다: {str(e)}"
        }

def product_analysis_node(state: AgentState, llm) -> AgentState:
    """
    제품 관련 검색 및 분석을 위한 특화 노드
    """
    try:
        product_name = state["input"]
        
        # 제품 관련 검색 쿼리 생성
        search_queries = [
            f"{product_name} 트렌드 2025",
            f"{product_name} 시장 분석",
            f"{product_name} 소비자 리뷰"
        ]
        
        all_results = []
        search = WebSearch()
        
        for query in search_queries:
            docs = search.get_relevant_documents(query)
            for doc in docs:
                all_results.append(doc.page_content)
        
        web_results = "\n\n".join(all_results[:10])  # 최대 10개 결과만 사용
        
        # 제품 분석 프롬프트 생성
        prompt_text = f"""
        다음은 '{product_name}'에 대한 웹 검색 결과입니다:
        
        {web_results}
        
        위 정보를 바탕으로 다음 사항들을 분석해주세요:
        1. 현재 시장 트렌드
        2. 소비자 선호도
        3. 주요 특징 및 장점
        4. 마케팅 포인트
        5. 향후 전망
        
        분석 결과를 체계적으로 정리하여 제공해주세요.
        """
        
        result = llm.invoke({"question": prompt_text, "web_results": web_results})
        
        return {
            **state,
            "web_results": web_results,
            "result": result,
            "route": "product_analysis"
        }
        
    except Exception as e:
        print(f"product_analysis_node에서 오류 발생: {e}")
        return {
            **state,
            "web_results": "",
            "result": f"제품 분석 중 오류가 발생했습니다: {str(e)}"
        }
