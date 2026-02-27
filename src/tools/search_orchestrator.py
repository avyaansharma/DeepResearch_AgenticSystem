import asyncio
from typing import List
from tavily import TavilyClient
from ..models import Source
from ..config import TAVILY_API_KEY


ACADEMIC_DOMAINS = [
    "arxiv.org", 
    "researchgate.net", 
    "scholar.google.com", 
    "semanticscholar.org", 
    "nature.com", 
    "sciencemag.org", 
    "ieee.org",
    "acm.org",
    "springer.com",
    "wiley.com",
    "sagepub.com",
    "taylorandfrancis.com"
]


class SearchOrchestrator:
    def __init__(self):
        self.client = TavilyClient(api_key=TAVILY_API_KEY)

    async def search(self, queries: List[str], max_results: int = 5) -> List[Source]:
        # Implementation to aggregate search results and filter URLs
        tasks = [self._search_single(q, max_results) for q in queries]
        results = await asyncio.gather(*tasks)
        
        # Flatten and deduplicate Sources by URL
        unique_sources = {}
        for sublist in results:
            for source in sublist:
                if source.url not in unique_sources:
                    unique_sources[source.url] = source
        
        return list(unique_sources.values())

    async def _search_single(self, query: str, max_results: int) -> List[Source]:
        # Craft query to prioritize academic domains if not already present
        search_query = query
        if not any(domain in query for domain in ACADEMIC_DOMAINS):
            search_query = f"{query} site:arxiv.org OR site:ieeexplore.ieee.org OR site:dl.acm.org OR site:link.springer.com OR site:researchgate.net"


        try:
            # We'll use the sync client for now as Tavily Python SDK search is sync
            # In a production app, we'd use an async HTTP client to Tavily's API
            response = self.client.search(
                query=search_query, 
                search_depth="advanced", 
                max_results=max_results,
                include_raw_content=True
            )
            
            sources = []
            for res in response.get('results', []):
                sources.append(Source(
                    url=res['url'],
                    title=res.get('title'),
                    snippet=res.get('content'),
                    metadata={
                        "score": res.get('score'),
                        "published_date": res.get('published_date'),
                        "domain": res['url'].split('/')[2]
                    }
                ))
            return sources
        except Exception as e:
            print(f"Search error for {query}: {e}")
            return []

