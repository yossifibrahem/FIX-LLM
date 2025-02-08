import asyncio
from crawl4ai import *
import json

async def scrape_website(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return {
            "url": url,
            "title": result.metadata["title"],
            "content": result.markdown,
        }

async def scrape_multiple_websites(urls):
    try:
        tasks = [scrape_website(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        return json.dumps({"error": str(e)})
