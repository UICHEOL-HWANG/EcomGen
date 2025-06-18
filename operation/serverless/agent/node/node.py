from prompt.prompts import PromptChain
from state.agent_state import AgentState
from tools.search_retrieve import WebSearch
import os 
import logging

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")

def simple_search_node(state: AgentState, llm) -> AgentState:
    """
    웹 검색을 수행하고 LLM으로 답변을 생성하는 노드
    """
    try:
        query = state["input"]
        logging.info(f"\n처리 중인 질문: {query}")

        # 웹 검색 수행
        search = WebSearch()
        docs = search.get_relevant_documents(query)
        web_results = "\n\n".join([f"제목: {doc.metadata.get('title', 'No title')}\n내용: {doc.page_content}" for doc in docs])
        
        logging.info(f"웹 검색 결과 길이: {len(web_results)} 문자")

        # 프롬프트에 웹 검색 결과와 질문 전달
        logging.info("LLM 추론 시작...")
        result = llm.invoke({
            "question": query,
            "web_results": web_results
        })
        logging.info("LLM 추론 완료")

        return {
            **state,
            "web_results": web_results,
            "result": result
        }

    except Exception as e:
        logging.info(f"❌ search_node에서 오류 발생: {e}")
        return {
            **state,
            "web_results": "",
            "result": f"검색 중 오류가 발생했습니다: {str(e)}"
        }