import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedData:
    """Data class for scraped website information"""
    url: str
    title: str
    content: str
    meta_description: str = ""
    status_code: int = 200
    error: str = ""
    scrape_time: float = 0.0

class WebScraper:
    """Advanced web scraper with rate limiting, error handling, and concurrency support"""
    
    def __init__(self, 
                 delay_range: tuple = (1, 3),
                 timeout: int = 10,
                 max_retries: int = 3,
                 user_agent: str = None):
        """
        Initialize the web scraper
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            user_agent: Custom user agent string
        """
        self.delay_range = delay_range
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Try to find main content areas
        main_content = None
        for selector in ['main', 'article', '.content', '#content', '.post', '.entry']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Get text and clean it up
            text = main_content.get_text(separator=' ', strip=True)
            # Remove extra whitespace
            text = ' '.join(text.split())
            return text
        
        return soup.get_text(separator=' ', strip=True)

    def _rate_limit(self):
        """Apply rate limiting between requests"""
        if self.delay_range:
            delay = random.uniform(self.delay_range[0], self.delay_range[1])
            time.sleep(delay)

    def scrape_website(self, url: str) -> ScrapedData:
        """
        Scrape a single website
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedData object with scraped information
        """
        start_time = time.time()
        
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'https://' + url
            
            logger.info(f"Scraping: {url}")
            
            # Make request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            title = ""
            if soup.title:
                title = soup.title.string.strip() if soup.title.string else ""
            
            # Try to get title from h1 if title tag is empty
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)
            
            content = self._extract_content(soup)
            
            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '').strip()
            
            scrape_time = time.time() - start_time
            
            return ScrapedData(
                url=url,
                title=title,
                content=content,
                meta_description=meta_desc,
                status_code=response.status_code,
                scrape_time=scrape_time
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return ScrapedData(
                url=url,
                title="",
                content="",
                status_code=0,
                error=f"Request error: {str(e)}",
                scrape_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return ScrapedData(
                url=url,
                title="",
                content="",
                status_code=0,
                error=f"Parsing error: {str(e)}",
                scrape_time=time.time() - start_time
            )

    def scrape_multiple_websites(self, 
                                urls: List[str], 
                                max_workers: int = 5,
                                save_to_file: str = None) -> List[ScrapedData]:
        """
        Scrape multiple websites concurrently
        
        Args:
            urls: List of URLs to scrape
            max_workers: Maximum number of concurrent workers
            save_to_file: Optional filename to save results as JSON
            
        Returns:
            List of ScrapedData objects
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self._scrape_with_rate_limit, url): url 
                for url in urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                result = future.result()
                results.append(result)
                
                # Log progress
                logger.info(f"Completed {len(results)}/{len(urls)}: {result.url}")
        
        # Sort results by original URL order
        url_to_result = {result.url: result for result in results}
        ordered_results = [url_to_result.get(url) for url in urls if url_to_result.get(url)]
        
        # Save to file if requested
        if save_to_file:
            self.save_results(ordered_results, save_to_file)
        
        return ordered_results

    def _scrape_with_rate_limit(self, url: str) -> ScrapedData:
        """Scrape with rate limiting applied"""
        self._rate_limit()
        return self.scrape_website(url)

    def save_results(self, results: List[ScrapedData], filename: str):
        """Save results to JSON file"""
        try:
            # Convert dataclass objects to dictionaries
            data = [
                {
                    'url': result.url,
                    'title': result.title,
                    'content': result.content[:1000] + '...' if len(result.content) > 1000 else result.content,  # Truncate for JSON
                    'meta_description': result.meta_description,
                    'status_code': result.status_code,
                    'error': result.error,
                    'scrape_time': result.scrape_time
                }
                for result in results
            ]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

# Convenience functions for backward compatibility
def scrape_website(url: str) -> Dict[str, str]:
    """
    Simple scraping function for backward compatibility
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with url, title, and content
    """
    scraper = WebScraper()
    result = scraper.scrape_website(url)
    
    return {
        "url": result.url,
        "title": result.title,
        "content": result.content,
    }

def scrape_multiple_websites(urls: List[str]) -> List[Dict[str, str]]:
    """
    Simple multi-site scraping function for backward compatibility
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of dictionaries with url, title, and content
    """
    scraper = WebScraper()
    results = scraper.scrape_multiple_websites(urls)
    
    return [
        {
            "url": result.url,
            "title": result.title,
            "content": result.content,
        }
        for result in results
    ]

# Example usage and testing
if __name__ == "__main__":
    # Example 1: Simple scraping
    print("=== Simple Scraping Example ===")
    result = scrape_website("https://example.com")
    print(f"Title: {result['title']}")
    print(f"Content length: {len(result['content'])}")
    
    # Example 2: Advanced scraping with custom settings
    print("\n=== Advanced Scraping Example ===")
    scraper = WebScraper(
        delay_range=(0.5, 1.5),  # Faster scraping
        timeout=15,
        max_retries=2
    )
    
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://quotes.toscrape.com"
    ]
    
    results = scraper.scrape_multiple_websites(
        urls, 
        max_workers=3,
        save_to_file="scraping_results.json"
    )
    
    for result in results:
        print(f"\nURL: {result.url}")
        print(f"Title: {result.title}")
        print(f"Status: {result.status_code}")
        print(f"Content length: {len(result.content)}")
        print(f"Scrape time: {result.scrape_time:.2f}s")
        if result.error:
            print(f"Error: {result.error}")