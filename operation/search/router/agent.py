import os
from autogen import ConversableAgent, UserProxyAgent, register_function

from langchain_community.tools import DuckDuckGoSearchResults

from tavily import TavilyClient

os.environ["TAVILY_API_KEY"] = "api"

def tavily_search(query: str, max_results: int = 3) -> str:
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(query=query, max_results=max_results)
    results = []
    for result in response['results']:
        results.append(f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}\n")
    return "\n".join(results)


def duckduckgo_search(query: str, num_results: int = 3) -> str:
    results = DuckDuckGoSearchResults(output_format="list").invoke(query)

    formatted_results = []
    for result in results:
        formatted_results.append(f"Title: {result['title']}\nURL: {result['link']}\nBody: {result['snippet']}\n")

    return "\n".join(formatted_results)

search = "고구마 요리 방법"

local_llm_config = {
    "config_list": [
        {
            "model": "qwen2.5:3b",
            "api_type": "ollama",
            "base_url": "http://localhost:11434",
            "price": [0, 0],
        }
        ,
        {
            "model": "EcomGen-Llama:0.0.1v",
            "api_type": "ollama",
            "base_url": "http://localhost:11434",
            "price": [0, 0],
            "functions" : [
                {
                    "name" : "duckduckgo_search",
                    "description" : "custom_search"
                }
            ]
        },
        {
            "model" : "EcomGen:0.0.1v",
            "api_type" : "ollama",
            "base_url" : "http://localhost:11434",
            "price" : [0,0]
        }
    ],
    "cache_seed": None,
}

def main():
    tavily_result = tavily_search(search)
    duckduckgo_result = duckduckgo_search(search)

    researcher = ConversableAgent("agent",
                                 system_message="""
                                 당신은 사용자의 질문에 대해 검색하고 답변하는 AI 입니다. 검색어에 따른 결과 내용을 정리하고 검색어에 따른 출처 링크도 같이 저장하여 마크다운 형식으로 작성하며 한국어로 대답해주세요.
                                 
                                 예시)
                                 입력값 : 겨울철 건강관리
                                 
                                 title : ### 겨울철 건강관리 가이드 분석 및 요약 (Markdown 형식)
                                    
                                    #### 1. **겨울철 건강관리 가이드**
                                    - URL: https://dangdangharu.co.kr/214
                                    - **주요 내용**:
                                      - **결론**: 겨울철 건강 유지의 핵심 실천 요소 강조
                                      - **핵심 포인트**:
                                        - **체온 유지**: 겨울 환경에 적합한 옷차림 및 생활 습관
                                        - **균형 잡힌 식단**: 영양소가 풍부한 식사로 면역력 강화
                                        - **규칙적인 운동**: 체력 유지 및 스트레스 해소
                                        - **적절한 수면**: 건강한 수면 패턴으로 인한 회복 증진
                                        - **위생 관리**: 감기 및 기타 감염 예방을 위한 철저한 관리
                                    
                                    #### 2. **겨울철 건강관리 꿀팁 10가지**
                                    - URL:   https://www.10000recipe.com/recipe/7012110
                                    - **주요 내용**:
                                      - **시즌적 중요성**: 추운 날씨로 인한 피로와 면역력 저하 강조
                                      - **주요 팁**:
                                        - **영양가 높은 식사**: 면역력 증진을 위한 식단 구성
                                        - **규칙적인 운동**: 체온 상승 및 체력 유지
                                        - **기타**: 구체적인 세부 팁들은 제시되지 않았으나, 건강 유지에 초점을 맞추고 있음
                                    
                                    #### 3. **겨울철 건강관리 주의사항 및 예방법**
                                    - URL: https://in.naver.com/wooamommy/topic/797522710422048
                                    - **주요 내용**:
                                      - **정신 건강 관리**:
                                        - **계절성 우울증 예방**:
                                          - **예방 방법**:
                                            - **햇볕 쬐기**: 오전 시간대에 최소 30분 이상 햇빛 노출로 세로토닌 분비 촉진
                                            - **추가 조언**: 자연광 노출은 정신 건강에 긍정적인 영향을 미침을 강조
                                    
                                    
                                 """,
                                 llm_config=local_llm_config["config_list"][0])

    validatior = ConversableAgent("translator",
                                      system_message=f"""
                                      당신은 이전 보고서를 참고하고 논리적으로 문제가 없는지 검증해주고 문장을 가다듬어주세요 또한 한국어로 나오게 교정해주세요.
                                      그리고 추가 검색 기능이 담긴 {duckduckgo_result}의 내용을 토대로 보고서를 작성해주세요. 
                                      """,
                                      llm_config=local_llm_config["config_list"][2])

    editor = ConversableAgent("summarizer",
                                      system_message="당신은 이전에 정리된 정보를 요약하고 마크다운 형태로 보고서를 작성해주는 전문가 입니다. 제목, 소제목, 내용 그리고 출처 링크까지 정리해서 마크다운 형태로 보고해주세요.",
                                      llm_config=local_llm_config["config_list"][2])
    register_function(
        tavily_search,
        caller=researcher,
        executor=researcher,
        name="tavily_search",
        description="A tool to search the internet using the Tavily API",
    )

    chat_result = researcher.initiate_chat(
        validatior, editor,
        message=f"{tavily_result}검색도구를 기반으로 검색하고 분석하여 마크다운 형식으로 보고서를 작성해주세요 검색기능이 있으니 활용 부탁드립니다.",
        summary_method="reflection_with_llm",
        max_turns=3
    )

    translator_msgs = [msg for msg in chat_result.chat_history if msg.get("name") == "translator"]

    if translator_msgs:
        return translator_msgs[0]["content"]
    return None




if __name__ == "__main__":
    print(main())