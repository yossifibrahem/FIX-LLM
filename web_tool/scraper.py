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


crawl_config = CrawlerRunConfig(
    exclude_external_images=True,         # Exclude external images
        exclude_external_links=True,          # No links outside primary domain
        exclude_social_media_links=True       # Skip recognized social media domains
    )

async def scrape_website_with_crawler(crawler, url):
    result = await crawler.arun(url=url, config=crawl_config)
    return {
        "url": url,
        "title": result.metadata["title"],
        "content": clean_markdown_content(result.markdown),
    }

async def scrape_multiple_websites(urls):
    """
    This function enables asynchronous web scraping for GPT models. It fetches the text content of multiple webpages concurrently and returns the results. Use this function when user queries include multiple URLs.

    Args:
        urls (list): A list of URLs to scrape.

    Returns:
        list: A list of dictionaries, each containing 'url', 'title', and 'content' of the scraped webpage.
        str: In case of an error, returns a JSON-formatted string with an error message.
    """

    try:
        async with AsyncWebCrawler() as crawler:
            tasks = [scrape_website_with_crawler(crawler, url) for url in urls]
            results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        return json.dumps({"error": str(e)})