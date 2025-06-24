import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import time

# Precompile regex patterns for performance.
IMAGE_PATTERN = re.compile(r'!\[.*?\]\(.*?\)')
INLINE_IMAGE_PATTERN = re.compile(r'<img.*?>', re.IGNORECASE)
VIDEO_PATTERN = re.compile(r'<video.*?</video>', re.DOTALL | re.IGNORECASE)
AUDIO_PATTERN = re.compile(r'<audio.*?</audio>', re.DOTALL | re.IGNORECASE)
PICTURE_PATTERN = re.compile(r'<picture.*?</picture>', re.DOTALL | re.IGNORECASE)
LINK_PATTERN = re.compile(r'\[(.*?)\]\(.*?\)')

def clean_text_content(text: str) -> str:
    """
    Clean text content by removing media elements and unnecessary formatting.
    """
    if not text:
        return ""
    
    text = IMAGE_PATTERN.sub('', text)
    text = INLINE_IMAGE_PATTERN.sub('', text)
    text = VIDEO_PATTERN.sub('', text)
    text = AUDIO_PATTERN.sub('', text)
    text = PICTURE_PATTERN.sub('', text)
    text = LINK_PATTERN.sub(r'\1', text)
    
    # Clean up extra whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def scrape_website_sync(url, timeout=10):
    """
    Scrape a single website synchronously using requests and BeautifulSoup.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Get title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Get main content
        content = ""
        
        # Try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body', re.I))
        
        if main_content:
            content = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback to body content
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
        
        # Clean the content
        cleaned_content = clean_text_content(content)
        
        return {
            "url": url,
            "title": title_text,
            "content": cleaned_content[:10000],  # Limit content size
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Failed to scrape website: {str(e)}"
        }
    except Exception as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Error processing website: {str(e)}"
        }

def scrape_multiple_websites(urls):
    """
    Scrape multiple websites synchronously.
    
    :param urls: A list of URLs to scrape.
    :return: A list of dictionaries, where each dictionary contains 'url', 'title', and 'content' of the scraped webpage.
             In case of an error, it returns a JSON-formatted string with an error message.
    """
    try:
        results = []
        for url in urls:
            result = scrape_website_sync(url)
            results.append(result)
            time.sleep(0.5)  # Be respectful to servers
        return results
    except Exception as e:
        return [{"url": "error", "title": "Error", "content": str(e)}]