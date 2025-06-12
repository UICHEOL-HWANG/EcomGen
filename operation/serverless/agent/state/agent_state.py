from typing import TypedDict, Optional

class AgentState(TypedDict, total=False):
    input: str # 사용자 입력
    web_results: Optional[str] # 웹 검색
    prompt: Optional[str] # 에이전트에게 주어지는 프롬프트
    result: Optional[str] # 결과 