from ast import Import
import json
import asyncio

# from web_tool.duck_duck_go_search import DuckDuckGoSearchManager
from web_tool.search import AdvancedSearchEngine
from web_tool.web_scraper import (
    scrape_website,
    WebScraper
)

scraper = WebScraper(
    delay_range=(0.5, 1.5),
    timeout=5,
    max_retries=2
)
search_engine = AdvancedSearchEngine(max_requests_per_minute=10)

def text_search(query: str, num_websites: int = 10) -> str:
    try:
        num_websites = min(num_websites, 20)  # Maximum 20 websites

        # Get URLs first
        URLs = search_engine.search_with_retry(query, num_websites, max_retries=2)
        
        # Scrape content from the websites
        scraped_content = []
        for url in URLs:
            try:
                content = scrape_website(url)
                scraped_content.append(content)
            except Exception as e:
                # If scraping fails, add error information
                scraped_content.append({
                    "url": url,
                    "content": f"Error scraping content: {str(e)}"
                })
        
        return json.dumps(scraped_content)
    except Exception as e:
        return json.dumps({"error": str(e)})
    

def webpage_scraper(url):
    """Scrape a webpage for its text content.

    This function enables web scraping for GPT models. It fetches the text content of a webpage and returns it to the
    model. Use this function if user queries include a URL.

    :param url: The URL of the webpage to scrape.
    :return: A JSON-formatted string containing the scraped text. In case of an error, it returns a JSON-formatted string with an error message.
    """
    try:
        result = scrape_website(url)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})
