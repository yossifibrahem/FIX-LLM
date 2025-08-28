import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
import time
import random
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, parse_qs, unquote
import re
from datetime import datetime
import json
from dataclasses import dataclass, asdict
import threading
from queue import Queue
import asyncio
import aiohttp
import concurrent.futures

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class for search results."""
    title: str
    url: str
    description: str
    timestamp: str = ''
    fetch_status: str = 'success'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

class RateLimiter:
    """Rate limiter to control request frequency."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """Check if a request can be made."""
        with self.lock:
            now = time.time()
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a request."""
        with self.lock:
            self.requests.append(time.time())
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded."""
        while not self.can_make_request():
            logger.info("Rate limit exceeded, waiting...")
            time.sleep(1)
        self.record_request()

class AdvancedSearchEngine:
    """
    Advanced search engine with multiple fallback strategies and anti-detection.
    """
    
    def __init__(self, max_requests_per_minute: int = 10):
        """Initialize the search engine."""
        self.base_url = 'https://www.google.com/search'
        self.rate_limiter = RateLimiter(max_requests_per_minute, 60)
        self.session = requests.Session()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0'
        ]
        
        # Initialize session with persistent settings
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Get randomized headers to avoid detection."""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.google.com',
        }
        
        # Add random Chrome-specific headers
        if 'Chrome' in headers['User-Agent']:
            headers.update({
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"' if 'Mac' in headers['User-Agent'] else '"Windows"',
            })
        
        return headers
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize search query."""
        # Remove special characters that might cause issues
        sanitized = re.sub(r'[^\w\s\-\+\.\,\?\!\"\'\(\)]', '', query)
        return sanitized.strip()
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp for results."""
        return datetime.now().isoformat()
    
    def _is_bot_detection_page(self, html: str) -> bool:
        """Check if the page is a bot detection page."""
        bot_indicators = [
            'enablejs', 'Please click here', 'unusual traffic',
            'captcha', 'robot', 'automated', 'verify you are human',
            'suspicious activity', 'blocked', 'access denied'
        ]
        
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in bot_indicators)
    
    def _add_human_delay(self, min_delay: float = 0.5, max_delay: float = 1.5):
        """Add random delay to mimic human behavior."""
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Adding human delay: {delay:.2f} seconds")
        time.sleep(delay)
    
    def search(self, query: str, num_results: int = 5, timeout: int = 10) -> List[SearchResult]:
        """
        Perform search with multiple fallback strategies.
        
        Args:
            query: Search query
            num_results: Maximum number of results
            timeout: Request timeout in seconds
            
        Returns:
            List of search results
        """
        sanitized_query = self._sanitize_query(query)
        logger.info(f"Starting search for query: '{sanitized_query}'")
        
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Try multiple approaches
        approaches = [
            self._try_google_search,
            self._try_alternative_google_search,
            self._try_duckduckgo_search
        ]
        
        for i, approach in enumerate(approaches):
            try:
                logger.info(f"Trying approach {i+1}: {approach.__name__}")
                results = approach(sanitized_query, num_results, timeout)
                
                if results:
                    logger.info(f"Found {len(results)} results with {approach.__name__}")
                    return results
                else:
                    logger.warning(f"{approach.__name__} returned no results")
                    
            except Exception as e:
                logger.error(f"{approach.__name__} failed: {str(e)}")
                continue
        
        logger.warning("All search approaches failed, returning empty results")
        return []
    
    def _try_google_search(self, query: str, num_results: int, timeout: int) -> List[SearchResult]:
        """Primary Google search approach."""
        logger.info("Attempting primary Google search...")
        
        # Add human-like delay
        self._add_human_delay(0.5, 1.5)
        
        params = {
            'q': query,
            'num': min(num_results, 10),
            'hl': 'en',
            'safe': 'off',
            'source': 'hp',
            'biw': '1920',
            'bih': '969',
            'tbm': '',
            'ie': 'UTF-8',
            'oe': 'UTF-8',
        }
        
        headers = self._get_random_headers()
        
        try:
            response = self.session.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            logger.info(f"Got response with status: {response.status_code}")
            logger.debug(f"Response length: {len(response.text)} characters")
            
            # Check for bot detection
            if self._is_bot_detection_page(response.text):
                logger.warning("Bot detection page detected")
                raise Exception("Bot detection page received")
            
            # Log HTML sample for debugging
            html_sample = response.text[:500]
            logger.debug(f"HTML sample: {html_sample}")
            
            results = self._parse_google_results(response.text, num_results)
            logger.info(f"Parsed {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Primary Google search failed: {str(e)}")
            raise
    
    def _try_alternative_google_search(self, query: str, num_results: int, timeout: int) -> List[SearchResult]:
        """Alternative Google search with different parameters."""
        logger.info("Attempting alternative Google search...")
        
        # Add longer delay for alternative approach
        self._add_human_delay(1.0, 3.0)
        
        params = {
            'q': query,
            'num': min(num_results, 10),
            'hl': 'en',
            'safe': 'off',
            'pws': '0',  # Disable personalized results
            'filter': '0',  # Disable duplicate filtering
            'start': '0',
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'gws_rd': 'cr',
        }
        
        headers = self._get_random_headers()
        headers.update({
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        
        try:
            response = self.session.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            logger.info(f"Alternative approach got response with status: {response.status_code}")
            
            # Check for bot detection
            if self._is_bot_detection_page(response.text):
                logger.warning("Alternative approach also got bot detection page")
                raise Exception("Bot detection page received")
            
            results = self._parse_google_results(response.text, num_results)
            logger.info(f"Alternative approach parsed {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Alternative Google search failed: {str(e)}")
            raise
    
    def _try_duckduckgo_search(self, query: str, num_results: int, timeout: int) -> List[SearchResult]:
        """DuckDuckGo search as fallback."""
        logger.info("Attempting DuckDuckGo search...")
        
        try:
            # Method 1: Use DDGS library
            try:
                ddgs = DDGS()
                results = ddgs.text(query, max_results=num_results)
                
                search_results = []
                timestamp = self._generate_timestamp()
                
                for result in results:
                    search_results.append(SearchResult(
                        title=result.get('title', ''),
                        url=result.get('href', ''),
                        description=result.get('body', ''),
                        timestamp=timestamp,
                        fetch_status='success'
                    ))
                
                logger.info(f"DuckDuckGo library returned {len(search_results)} results")
                return search_results
                
            except Exception as e:
                logger.warning(f"DuckDuckGo library failed: {str(e)}, trying HTML scraping")
                
                # Method 2: HTML scraping fallback
                return self._scrape_duckduckgo_html(query, num_results, timeout)
                
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            raise
    
    def _scrape_duckduckgo_html(self, query: str, num_results: int, timeout: int) -> List[SearchResult]:
        """Scrape DuckDuckGo HTML directly."""
        logger.info("Scraping DuckDuckGo HTML...")
        
        url = 'https://html.duckduckgo.com/html/'
        params = {'q': query}
        headers = self._get_random_headers()
        
        response = self.session.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        logger.info(f"DuckDuckGo HTML got response with status: {response.status_code}")
        
        results = self._parse_duckduckgo_results(response.text, num_results)
        logger.info(f"DuckDuckGo HTML parsed {len(results)} results")
        
        return results
    
    def _parse_google_results(self, html: str, max_results: int) -> List[SearchResult]:
        """Parse Google search results with comprehensive selectors."""
        logger.info(f"Parsing Google HTML with length: {len(html)}")
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        timestamp = self._generate_timestamp()
        
        # Multiple selector strategies
        search_result_selectors = [
            'div.g',
            'div[data-sokoban-container]',
            '.tF2Cxc',
            '.rc',
            '[data-ved]',
            'div[jscontroller]'
        ]
        
        # Log what we find
        for selector in search_result_selectors:
            elements = soup.select(selector)
            logger.debug(f"Found {len(elements)} elements with selector: {selector}")
        
        found_results = False
        
        for selector in search_result_selectors:
            if found_results and results:
                break
            
            logger.debug(f"Trying selector: {selector}")
            elements = soup.select(selector)
            
            for element in elements:
                if len(results) >= max_results:
                    break
                
                # Try multiple title selectors
                title_selectors = ['h3', '.LC20lb', '.DKV0Md', 'a[data-ved]', '.r']
                title = ''
                url = ''
                
                for title_selector in title_selectors:
                    title_elem = element.select_one(title_selector)
                    if title_elem:
                        title = title_elem.get_text().strip()
                        logger.debug(f"Found title with {title_selector}: '{title}'")
                        
                        # Find associated link
                        link_elem = title_elem.find_parent('a') or title_elem.find('a')
                        if link_elem:
                            url = link_elem.get('href', '')
                            logger.debug(f"Found URL: '{url}'")
                        else:
                            # Try to find any link in the element
                            any_link = element.select_one('a[href]')
                            if any_link:
                                url = any_link.get('href', '')
                                logger.debug(f"Found URL from any link: '{url}'")
                        break
                
                # Try multiple snippet selectors
                snippet_selectors = [
                    '.VwiC3b', '.st', '.aCOpRe', '.IsZvec', 
                    '.s3v9rd', '.MUxGbd', '.snippet-content'
                ]
                description = ''
                
                for snippet_selector in snippet_selectors:
                    snippet_elem = element.select_one(snippet_selector)
                    if snippet_elem:
                        description = snippet_elem.get_text().strip()
                        logger.debug(f"Found snippet with {snippet_selector}: '{description[:100]}...'")
                        break
                
                if title and url and self._is_valid_search_url(url):
                    clean_url = self._clean_google_url(url)
                    logger.debug(f"Adding result: {title}")
                    results.append(SearchResult(
                        title=title,
                        url=clean_url,
                        description=description or 'No description available',
                        timestamp=timestamp,
                        fetch_status='success'
                    ))
                    found_results = True
                else:
                    logger.debug(f"Skipping result: title='{title}', url='{url}', valid={self._is_valid_search_url(url)}")
        
        # Aggressive fallback: look for any h3 with links
        if not results:
            logger.info("No results found, trying aggressive h3 search...")
            h3_elements = soup.select('h3')
            
            for h3 in h3_elements:
                if len(results) >= max_results:
                    break
                
                title = h3.get_text().strip()
                link = h3.find_parent('a') or h3.find('a')
                
                if link and title:
                    url = link.get('href', '')
                    logger.debug(f"Aggressive search found: '{title}' -> '{url}'")
                    
                    if self._is_valid_search_url(url):
                        results.append(SearchResult(
                            title=title,
                            url=self._clean_google_url(url),
                            description='No description available',
                            timestamp=timestamp,
                            fetch_status='success'
                        ))
        
        logger.info(f"Google parsing found {len(results)} results")
        return results
    
    def _parse_duckduckgo_results(self, html: str, max_results: int) -> List[SearchResult]:
        """Parse DuckDuckGo search results."""
        logger.info(f"Parsing DuckDuckGo HTML with length: {len(html)}")
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        timestamp = self._generate_timestamp()
        
        # DuckDuckGo results are in .result elements
        result_elements = soup.select('.result')
        logger.debug(f"Found {len(result_elements)} .result elements")
        
        for element in result_elements:
            if len(results) >= max_results:
                break
            
            # Extract title and URL
            title_elem = element.select_one('.result__title a')
            if not title_elem:
                continue
            
            title = title_elem.get_text().strip()
            url = title_elem.get('href', '')
            
            # Extract snippet
            snippet_elem = element.select_one('.result__snippet')
            description = snippet_elem.get_text().strip() if snippet_elem else ''
            
            if title and url:
                clean_url = self._clean_duckduckgo_url(url)
                logger.debug(f"DuckDuckGo found: '{title}' -> '{clean_url}'")
                results.append(SearchResult(
                    title=title,
                    url=clean_url,
                    description=description or 'No description available',
                    timestamp=timestamp,
                    fetch_status='success'
                ))
        
        logger.info(f"DuckDuckGo parsing found {len(results)} results")
        return results
    
    def _is_valid_search_url(self, url: str) -> bool:
        """Check if URL is valid for search results."""
        if not url:
            return False
        
        # Google search results URLs can be in various formats
        valid_patterns = [
            url.startswith('/url?'),
            url.startswith('http://'),
            url.startswith('https://'),
            url.startswith('//'),
            url.startswith('/search?'),
            url.startswith('/'),
            'google.com' in url,
            len(url) > 10
        ]
        
        return any(valid_patterns)
    
    def _clean_google_url(self, url: str) -> str:
        """Clean Google's redirect URLs."""
        if url.startswith('/url?'):
            try:
                # Parse the redirect URL
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                # Try different parameter names
                for param in ['q', 'url']:
                    if param in params:
                        actual_url = params[param][0]
                        return unquote(actual_url)
                        
            except Exception as e:
                logger.warning(f"Failed to parse Google redirect URL: {url}, error: {str(e)}")
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            return 'https:' + url
        
        # Handle relative URLs
        if url.startswith('/') and not url.startswith('//'):
            return 'https://www.google.com' + url
        
        return url
    
    def _clean_duckduckgo_url(self, url: str) -> str:
        """Clean DuckDuckGo's redirect URLs."""
        if url.startswith('//duckduckgo.com/l/'):
            try:
                # Extract the uddg parameter
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                if 'uddg' in params:
                    actual_url = params['uddg'][0]
                    decoded_url = unquote(actual_url)
                    logger.debug(f"Decoded DuckDuckGo URL: {decoded_url}")
                    return decoded_url
                    
            except Exception as e:
                logger.warning(f"Failed to decode DuckDuckGo URL: {url}, error: {str(e)}")
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            return 'https:' + url
        
        return url
    
    def search_with_retry(self, query: str, num_results: int = 5, 
                         max_retries: int = 3, delay: float = 2.0) -> List[SearchResult]:
        """
        Search with retry mechanism.
        
        Args:
            query: Search query
            num_results: Number of results to return
            max_retries: Maximum retry attempts
            delay: Delay between retries
            
        Returns:
            List of search results
        """
        for attempt in range(max_retries + 1):
            try:
                results = self.search(query, num_results)
                
                if results:
                    return results
                elif attempt < max_retries:
                    logger.info(f"No results found, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(delay)
                    
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Search attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All search attempts failed: {str(e)}")
        
        return []
    
    def export_results(self, results: List[SearchResult], format: str = 'json') -> str:
        """Export search results to different formats."""
        if format.lower() == 'json':
            return json.dumps([result.to_dict() for result in results], indent=2)
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Title', 'URL', 'Description', 'Timestamp'])
            
            # Write data
            for result in results:
                writer.writerow([result.title, result.url, result.description, result.timestamp])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

# # Example usage
# if __name__ == "__main__":
#     # Initialize the search engine
#     search_engine = AdvancedSearchEngine(max_requests_per_minute=10)
    
#     # Example searches
#     queries = [
#         "machine learning algorithms comparison",
#     ]
    
#     for query in queries:
#         print(f"\n{'='*60}")
#         print(f"Searching for: '{query}'")
#         print(f"{'='*60}")
        
#         # Search with retry
#         results = search_engine.search_with_retry(query, num_results=5, max_retries=2)
        
#         if results:
#             print(f"\nFound {len(results)} results:")
#             for i, result in enumerate(results, 1):
#                 print(f"\n{i}. {result.title}")
#                 print(f"   URL: {result.url}")
#                 print(f"   Description: {result.description[:100]}...")
#                 print(f"   Timestamp: {result.timestamp}")
#         else:
#             print("\nNo results found.")
