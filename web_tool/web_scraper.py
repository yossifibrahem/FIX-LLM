import json
import logging
import re

import requests
from bs4 import BeautifulSoup

# Configure logging
logging = logging.getLogger(__name__)


class WebContentScraper:
    def __init__(self, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"):
        self.headers = {"User-Agent": user_agent}

    def _fetch_page_content(self, url):
        """Fetches the content of a web page from a given URL."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return None
        except Exception as err:
            logging.error(f"Error occurred: {err}")
            return None

    def _parse_web_content(self, content):
        """Parses HTML content and extracts text and title."""
        try:
            soup = BeautifulSoup(content, "html.parser")
            # Extract title
            title = soup.title.string if soup.title else "No title found"
            # Extract paragraphs
            paragraphs = soup.find_all("p")
            content = "\n".join(paragraph.get_text() for paragraph in paragraphs)
            return title.strip(), content
        except Exception as e:
            logging.error(f"Failed to parse the content: {e}")
            return None, None

    def preprocess_text(self, text):
        text = re.sub(r'\[\d+\]', '', text)
        text = '\n'.join([' '.join(line.split()) for line in text.split('\n') if line.strip()])
        return text

    def scrape_website(self, url):
        """Scrapes the content and title from a given website URL."""
        logging.debug(f"Scraping URL: {url}")
        page_content = self._fetch_page_content(url)
        if page_content:
            title, parsed_content = self._parse_web_content(page_content)
            if parsed_content:
                parsed_content = self.preprocess_text(parsed_content)
                return {
                    "url": url,
                    "title": title,
                    "content": parsed_content
                }
            else:
                return {"url": url, "error": "Failed to parse content"}
        return {"url": url, "error": "Failed to fetch page content"}

    def scrape_multiple_websites(self, urls):
        """Scrapes the content from multiple websites."""
        try:
            content = []
            for url in urls:
                content.append(self.scrape_website(url))
            return content
        except Exception as e:
            logging.error(f"Error during scraping multiple websites: {e}")
            return json.dumps({"error": str(e)})