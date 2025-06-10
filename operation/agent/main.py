import runpod
from langgraph.graph import END, StateGraph
import os
import logging

from state.agent_state import AgentState
from chaining.chain import create_chaining
from prompt.prompts import PromptChain
from initialized.model_initialized import ModelInitialized
from node.node import simple_search_node, product_analysis_node
from langchain_core.output_parsers import StrOutputParser

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 설정
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "false")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "")

# 전역 변수로 모델과 워크플로우 초기화 (컨테이너 재사용을 위해)
_model = None
_workflow = None

def initialize_model():
    """모델 전역으로 초기화"""
    global _model
    if _model is None:
        logger.info("모델 초기화 시작...")
        _model = ModelInitialized()
        logger.info("모델 초기화 완료")
    return _model

def initialize_workflow():
    """워크플로우를 전역으로 초기화"""
    global _workflow
    if _workflow is None:
        logger.info("워크플로우 초기화 시작...")
        
        # 모델 초기화
        model = initialize_model()
        
        # 검색 체인 생성
        search_chain = create_chaining(
            prompt=PromptChain().search_prompt,
            model=model(),  # __call__ 메서드로 LLM 객체 반환
            parser=StrOutputParser()
        )
        
        # 노드 함수들을 정의
        def search_node(state):
            return simple_search_node(state, llm=search_chain)
        
        def product_node(state):
            return product_analysis_node(state, llm=search_chain)
        
        def router(state):
            """라우팅 로직"""
            input_text = state["input"].lower()
            
            # 제품 관련 키워드 체크
            product_keywords = ["제품", "상품", "브랜드", "패션", "트렌드", "리뷰", "분석"]
            
            if any(keyword in input_text for keyword in product_keywords):
                return "product_analysis"
            else:
                return "general_search"
        
        # 워크플로우 구성
        workflow = StateGraph(AgentState)
        
        # 노드 추가
        workflow.add_node("router", router)
        workflow.add_node("general_search", search_node)
        workflow.add_node("product_analysis", product_node)
        
        # 엣지 설정
        workflow.set_entry_point("router")
        
        # 조건부 엣지 (라우터 결과에 따라 분기)
        workflow.add_conditional_edges(
            "router",
            lambda state: router(state),
            {
                "general_search": "general_search",
                "product_analysis": "product_analysis"
            }
        )
        
        # 종료 지점 설정
        workflow.add_edge("general_search", END)
        workflow.add_edge("product_analysis", END)
        
        _workflow = workflow.compile()
        logger.info("워크플로우 초기화 완료")
    
    return _workflow

def handler(job):
    """
    RunPod Serverless 핸들러
    
    입력 형태:
    {
        "input": {
            "query": "사용자 질문",
            "type": "search" | "product_analysis" (선택사항)
        }
    }
    """
    try:
        # 입력 파라미터 추출
        job_input = job.get("input", {})
        query = job_input.get("query", "")
        analysis_type = job_input.get("type", "auto")  # auto, search, product_analysis
        
        if not query:
            return {
                "error": "query 파라미터가 필요합니다.",
                "status": "failed"
            }
        
        logger.info(f"처리 시작 - Query: {query}, Type: {analysis_type}")
        
        # 워크플로우 초기화
        app = initialize_workflow()
        
        # 상태 생성
        state = {"input": query}
        
        # 특정 타입이 지정된 경우 라우팅 강제
        if analysis_type == "product_analysis":
            state["route"] = "product_analysis"
        elif analysis_type == "search":
            state["route"] = "general_search"
        
        # 워크플로우 실행
        result = app.invoke(state)
        
        logger.info("처리 완료")
        
        return {
            "result": result.get("result", ""),
            "web_results": result.get("web_results", ""),
            "route": result.get("route", "unknown"),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
        return {
            "error": f"처리 중 오류가 발생했습니다: {str(e)}",
            "status": "failed"
        }

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
