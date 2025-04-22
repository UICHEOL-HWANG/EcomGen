from langchain_community.tools import TavilySearchResults

def tavily_search(query: str, max_results: int = 3) -> str:
    """

    :param query: 작성자의 질문 내용
    :param max_results: 총 몇개의 결과물을 원하는지 예시 3개
    :return: TavilySearchResults 결과 반환
    """
    client = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )



    response = client.invoke({"query": query})
    results = []

    for result in response:
        results.append(f"URL: {result['url']}\nContent: {result['content']}\n")
    return "\n".join(results)