from langchain.prompts import ChatPromptTemplate, PromptTemplate

class PromptChain:

    def __init__(self):

        self.search_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "당신은 최신 정보를 바탕으로 정확하고 포괄적인 보고서를 작성하는 전문가입니다.\n\n"
             "아래의 지침에 따라 보고서를 작성해주세요:\n"
             "1. 보고서는 반드시 한국어로 작성되어야 합니다.\n"
             "2. 서론에서는 질문의 배경과 목적을 간략히 설명합니다.\n"
             "3. 본론에서는 웹 검색 결과를 토대로 주요 정보, 데이터, 분석 결과를 체계적으로 정리합니다.\n"
             "4. 결론에서는 주요 발견 사항과 제언을 명확하게 제시합니다.\n"
             "5. 각 정보의 출처를 명시하고, 최신 정보를 우선시하여 반영합니다.\n\n"
             "질문: {question}\n"
             "웹 검색 결과: {web_results}"),
            ("user", "{question}")
        ])
