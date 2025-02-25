import asyncio
from crawl4ai import *
import json
import re

# Precompile regex patterns for performance.
IMAGE_PATTERN = re.compile(r'!\[.*?\]\(.*?\)')
INLINE_IMAGE_PATTERN = re.compile(r'<img.*?>')
VIDEO_PATTERN = re.compile(r'<video.*?</video>', re.DOTALL)
AUDIO_PATTERN = re.compile(r'<audio.*?</audio>', re.DOTALL)
PICTURE_PATTERN = re.compile(r'<picture.*?</picture>', re.DOTALL)
LINK_PATTERN = re.compile(r'\[(.*?)\]\(.*?\)')

def clean_markdown_content(text: str) -> str:
    """
    Clean markdown content by removing media elements and unnecessary formatting.
    """
    text = IMAGE_PATTERN.sub('', text)
    text = INLINE_IMAGE_PATTERN.sub('', text)
    text = VIDEO_PATTERN.sub('', text)
    text = AUDIO_PATTERN.sub('', text)
    text = PICTURE_PATTERN.sub('', text)
    text = LINK_PATTERN.sub(r'\1', text)
    return text.strip()

async def scrape_website_with_crawler(crawler, url):
    result = await crawler.arun(url=url)
    return {
        "url": url,
        "title": result.metadata["title"],
        "content": clean_markdown_content(result.markdown),
    }

async def scrape_multiple_websites(urls):
    try:
        async with AsyncWebCrawler() as crawler:
            tasks = [scrape_website_with_crawler(crawler, url) for url in urls]
            results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        return json.dumps({"error": str(e)})