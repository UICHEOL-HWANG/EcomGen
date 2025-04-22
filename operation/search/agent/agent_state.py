from typing import TypedDict, List, Optional

class AgentSate(TypedDict):
    query: str
    research_result: str
    final_report: str
    score: Optional[int]
    improved_prompt: Optional[str]