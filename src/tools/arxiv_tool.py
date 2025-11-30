import arxiv
from tenacity import retry, stop_after_attempt, wait_exponential
from src.state import ArxivResult, AuthorStats
from typing import List

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def search_arxiv(keywords: List[str], min_year: int) -> List[ArxivResult]:
    print(f"🔍 Searching arXiv for keywords: {keywords}, min_year: {min_year}")
    query = " AND ".join(keywords)
    search = arxiv.Search(
        query=query,
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance
    )
    results = []
    for result in search.results():
        if result.published.year >= min_year:
            results.append(ArxivResult(
                title=result.title,
                authors=[a.name for a in result.authors],
                abstract=result.summary,
                published_year=result.published.year
            ))
    print(f"✅ Found {len(results)} papers.")
    return results

def author_stats(authors: List[str]) -> List[AuthorStats]:
    print(f"🔍 Fetching author stats for {len(authors)} authors")
    # Заглушка: в реальности это был бы вызов API или БД
    return [AuthorStats(h_index=10, total_papers=50) for _ in authors]