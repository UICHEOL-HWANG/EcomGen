from agent.chain import create_chaining
from agent.initialized_model import AgentInitialized
from agent.node import Node
from agent.prompt import PromptChain
from agent.agent_state import AgentSate

from functools import partial
from langgraph.graph import StateGraph
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

import os
from dotenv import load_dotenv

load_dotenv()


os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_API_KEY"] =  os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] =  os.getenv("LANGSMITH_PROJECT")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")

def main():
    # 체인 정의
    research_chain = create_chaining(
        prompt=PromptChain().report_prompt,
        model=AgentInitialized(model_name="timHan/llama3.2korean3B4QKM:latest"),
        parser=StrOutputParser()
    )

    validation_chain = create_chaining(
        prompt=PromptChain().validation_prompt,
        model=AgentInitialized(model_name="huihui_ai/kanana-nano-abliterated:2.1b", streaming=True),
        parser=JsonOutputParser()
    )

    # 노드 정의 (partial은 괄호만 닫으면 끝)
    researcher = partial(Node().researcher, chain=research_chain)
    validator = partial(Node().validator, chain=validation_chain)

    # 워크플로우 구성
    workflow = StateGraph(AgentSate)

    workflow.add_node("researcher", researcher)
    workflow.add_node("validator", validator)

    workflow.set_entry_point("researcher")
    workflow.set_finish_point("validator")

    workflow.add_edge("researcher", "validator")

    # 컴파일
    app = workflow.compile()

    return app

