import asyncio
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from ..models import Source


class CrawlerLayer:
    def __init__(self):
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            java_script_enabled=True
        )
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            stream=False
        )

    async def crawl_multiple(self, sources: List[Source]) -> List[Source]:
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            tasks = []
            for source in sources:
                tasks.append(crawler.arun(url=source.url, config=self.run_config))
            
            results = await asyncio.gather(*tasks)
            
            updated_sources = []
            for i, res in enumerate(results):
                source = sources[i]
                if res.success:
                    source.content = res.markdown_v2.raw_markdown if hasattr(res, 'markdown_v2') else res.markdown
                    # Basic metadata extraction if available
                    if res.metadata:
                        source.metadata.update(res.metadata)
                    updated_sources.append(source)
                else:
                    print(f"Failed to crawl {source.url}: {res.error_message}")
            
            return updated_sources

