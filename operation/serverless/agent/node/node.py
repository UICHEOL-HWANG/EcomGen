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
