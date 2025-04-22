from .agent_state import AgentSate
from .tools import tavily_search

import os
import json
from dotenv import load_dotenv

load_dotenv()

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

class Node:

    def researcher(self, state: AgentSate, chain):
        question = state["query"]
        search_tool = tavily_search(query=question, max_results=5)

        result = chain.invoke({
            "query": question,
            "document": search_tool
        })

        state["research_result"] = result
        return state

    def validator(self, state: AgentSate, chain):
        research_report = state["research_result"]

        # validation 프롬프트 실행
        validation_response = chain.invoke({
            "report": research_report
        })

        try:
            result_json = validation_response  # ✅ JsonOutputParser()가 이미 dict 반환함
            state["score"] = int(result_json.get("score", 0))
            state["improved_prompt"] = result_json.get("improved_prompt", "")
            state["final_report"] = research_report
        except Exception as e:
            state["score"] = 0
            state["improved_prompt"] = ""
            state["final_report"] = f"검토 중 오류 발생: {e}"

        return state

