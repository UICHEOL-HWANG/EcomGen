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

# 모델 전역 설정
_model = None

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 설정
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "false")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "")


def get_model():
    global _model
    if _model is None:
        _model = ModelInitialized()
    return _model


def main():
    logger.info("워크플로우 초기화 시작...")

    # 모델 초기화
    model = get_model()

    # 검색 체인 생성
    search_chain = create_chaining(
        prompt=PromptChain().search_prompt,
        model=model(),
        parser=StrOutputParser()
    )

    # 노드 정의
    def search_node(state):
        return simple_search_node(state, llm=search_chain)

    # 워크플로우 구성
    workflow = StateGraph(AgentState)
    workflow.add_node("general_search", search_node)
    workflow.set_entry_point("general_search")
    workflow.add_edge("general_search", END)

    compiled_workflow = workflow.compile()

    logger.info("워크플로우 초기화 완료")
    return compiled_workflow


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

        if not query:
            return {
                "error": "query 파라미터가 필요합니다.",
                "status": "failed"
            }

        # 워크플로우 초기화
        app = main()

        # 워크플로우 실행
        result = app.invoke({"input": query})

        logger.info("처리 완료")

        return {
            "result": result.get("result", ""),
            "web_results": result.get("web_results", ""),
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
