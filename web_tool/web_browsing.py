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

def text_search(query: str, num_websites: int = 5) -> str:
    """Conducts a general web text search and retrieves information from the internet in response to user queries.

    This function is best used when the user's query is seeking broad information available on various websites. It
    is ideal for queries that require diverse perspectives or data from multiple sources, not limited to current
    events or specific topics. Use this function for general inquiries, research, or when the user's query is not
    explicitly news-related. It fetches relevant data from the internet in response to user queries, enhancing GPT's
    knowledge base.

    :param query: The search query string.
    :param num_websites: The number of websites to search for the query. Defaults to 4 if not provided. (optional)

    :return: A dictionary containing the scraped content from the most relevant websites.
    """
    try:
        num_websites = min(num_websites, 8)  # Maximum 8 websites
        
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
