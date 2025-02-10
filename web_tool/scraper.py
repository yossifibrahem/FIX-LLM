import asyncio
from crawl4ai import *
import json
import re

async def scrape_website(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return {
            "url": url,
            "title": result.metadata["title"],
            "content": clean_markdown_content(result.markdown),
        }

async def scrape_multiple_websites(urls):
    try:
        tasks = [scrape_website(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        return json.dumps({"error": str(e)})

def clean_markdown_content(text: str) -> str:
    """
    Clean markdown content by removing media elements and unnecessary formatting.
    """
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove inline images
    text = re.sub(r'<img.*?>', '', text)
    # Remove video embeds
    text = re.sub(r'<video.*?</video>', '', text)
    # Remove audio embeds
    text = re.sub(r'<audio.*?</audio>', '', text)
    # Remove responsive images
    text = re.sub(r'<picture.*?</picture>', '', text)
    # Remove URLs but keep link text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # # Remove HTML comments
    # text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # # Remove code blocks
    # text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # # Remove inline code
    # text = re.sub(r'`.*?`', '', text)
    # # Remove multiple newlines
    # text = re.sub(r'\n\s*\n', '\n', text)
    # # Remove multiple spaces
    # text = re.sub(r'\s+', ' ', text)
    return text.strip()