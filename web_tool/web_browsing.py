import json
import asyncio

# from web_tool.duck_duck_go_search import DuckDuckGoSearchManager
from web_tool.search import AdvancedSearchEngine
from web_tool.scraper import scrape_multiple_websites
from web_tool.embedding_similarity import find_most_similar_content
from web_tool.web_scraper import (
    scrape_website,
    WebScraper
)

scraper = WebScraper(
    delay_range=(0.5, 1.5),
    timeout=5,
    max_retries=2
)
# ddg = DuckDuckGoSearchManager()
search_engine = AdvancedSearchEngine(max_requests_per_minute=10)

def text_search(query: str, keywords: list, full_context: bool = True, num_websites: int = 4, citations: int = 5) -> str:
    """Conducts a general web text search and retrieves information from the internet in response to user queries.

    This function is best used when the user's query is seeking broad information available on various websites. It
    is ideal for queries that require diverse perspectives or data from multiple sources, not limited to current
    events or specific topics. Use this function for general inquiries, research, or when the user's query is not
    explicitly news-related. It fetches relevant data from the internet in response to user queries, enhancing GPT's
    knowledge base.

    :param query: The search query string.
    :param keywords: The keywords to compare the search results against.
    :param num_websites: The number of websites to search for the query. Defaults to 4 if not provided. (optional)
    :param citations: The number of citations to return. Defaults to 5 if not provided. (optional)

    :return: A dictionary containing the URL and citation of the most relevant content.
    """
    try:
        num_websites = min(num_websites, 8)  # Maximum 8 websites
        citations = min(citations, 10)        # Maximum 10 citations
        
        # urls = ddg.text_search(query, int(num_websites))
        results = search_engine.search_with_retry(query, num_results=5, max_retries=2)
        urls = [result.url for result in results]
        scraped_data = asyncio.run(scrape_multiple_websites(urls))
        if full_context:
            return scraped_data
        filtered_data = find_most_similar_content(scraped_data, keywords, citations)
        return filtered_data
    except Exception as e:
        return {"url": "error", "citation": str(e)}
    

def text_search_bs4(query: str, keywords: list, full_context: bool = True, num_websites: int = 4, citations: int = 5) -> str:
    """Conducts a general web text search and retrieves information from the internet in response to user queries.

    This function is best used when the user's query is seeking broad information available on various websites. It
    is ideal for queries that require diverse perspectives or data from multiple sources, not limited to current
    events or specific topics. Use this function for general inquiries, research, or when the user's query is not
    explicitly news-related. It fetches relevant data from the internet in response to user queries, enhancing GPT's
    knowledge base.

    :param query: The search query string.
    :param keywords: The keywords to compare the search results against.
    :param num_websites: The number of websites to search for the query. Defaults to 4 if not provided. (optional)
    :param citations: The number of citations to return. Defaults to 5 if not provided. (optional)

    :return: A dictionary containing the URL and citation of the most relevant content.
    """
    try:
        num_websites = min(num_websites, 8)  # Maximum 8 websites
        citations = min(citations, 10)        # Maximum 10 citations
        
        # urls = ddg.text_search(query, int(num_websites))
        results = search_engine.search_with_retry(query, num_results=5, max_retries=2)
        urls = [result.url for result in results]
        scraped_data = scraper.scrape_multiple_websites(
            urls, 
            max_workers=3,
        )
        if full_context:
            return scraped_data
        filtered_data = find_most_similar_content(scraped_data, keywords, citations)
        return filtered_data
    except Exception as e:
        return {"url": "error", "citation": str(e)}    

