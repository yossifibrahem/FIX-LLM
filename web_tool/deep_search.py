from typing import List, Dict, Optional
from dataclasses import dataclass
from web_tool.duck_duck_go_search import DuckDuckGoSearchManager
from web_tool.scraper import scrape_multiple_websites
import asyncio
# import logging


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    title: str
    url: str
    summary: str

class DeepSearchManager:
    SYSTEM_PROMPT = """You are a professional content analyst. Given website content, provide a clear, factual summary that:
    - Extracts the main points relevant to the prompt
    - Maintains accuracy and context
    - Excludes redundant information
    - Uses concise, objective language
    - Avoids personal opinions or subjective interpretations
    - if the information is not exactly relevant to the prompt, please say "No relevant information found"
    
    prompt context: {prompt}
    
    Provide the summary in 3-5 sentences focusing on the most relevant information."""

    def __init__(self):
        self.search_manager = DuckDuckGoSearchManager()

    async def _generate_summary(
        self, 
        client,
        MODEL,
        content: str, 
        title: str, 
        url: str, 
        prompt: str
    ) -> Optional[SearchResult]:
        """Generate a summary for a single piece of content using the LLM."""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT.format(prompt=prompt)
                    },
                    {
                        "role": "user",
                        "content": f"Title: {title}\nURL: {url}\nContent: {content}"
                    }
                ],
                temperature=0.5
            )

            summary=response.choices[0].message.content

            while "<think>" in summary and "</think>" in summary:
                start = summary.find("<think>")
                end = summary.find("</think>") + len("</think>")
                summary = summary[:start] + summary[end:]

            return SearchResult(
                title=title,
                url=url,
                summary=summary
            )
        except Exception as e:
            # logger.error(f"Error generating summary for {url}: {str(e)}")
            return None

    async def deep_search(self, query: str, prompt: str, client, MODEL, num_results: int = 10) -> List[SearchResult]:
        """Perform a deep search and generate summaries for the results."""
        try:
            # Get search results
            urls = self.search_manager.text_search(query, num_results)
            if not urls:
                # logger.warning("No URLs found for the query")
                return []

            # Scrape websites
            scraped_data = await scrape_multiple_websites(urls)
            if not scraped_data:
                # logger.warning("No content scraped from URLs")
                return []

            # Generate summaries concurrently
            tasks = []
            for data in scraped_data:
                if content := data.get("content"):
                    task = self._generate_summary(
                        client=client,
                        MODEL=MODEL,
                        content=content,
                        title=data.get("title", ""),
                        url=data.get("url", ""),
                        prompt=prompt
                    )
                    tasks.append(task)

            # Wait for all summaries to be generated
            summaries = await asyncio.gather(*tasks)
            return [s for s in summaries if s is not None]

        except Exception as e:
            # logger.error(f"Error in deep search: {str(e)}")
            return []

# Create a singleton instance
deep_search_manager = DeepSearchManager()

# Main function to be called by other modules
async def deep_search(query: str, prompt: str, num_results: int, client, MODEL) -> List[Dict]:
    """Public interface for deep search functionality."""
    results = await deep_search_manager.deep_search(query, prompt, client, MODEL, num_results)
    return [{"title": r.title, "url": r.url, "summary": r.summary} for r in results]