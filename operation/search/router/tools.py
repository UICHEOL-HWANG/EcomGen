from langchain_community.tools import TavilySearchResults

def tavily_search(query: str, max_results: int = 3) -> str:
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