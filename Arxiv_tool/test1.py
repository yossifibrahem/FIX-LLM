import arxiv
from typing import Dict, Optional
import json

client = arxiv.Client()

def get_arxiv_papers_by_keyword(keyword: str, max_results: int = 1) -> Optional[Dict]:
    """
    Fetch papers from Arxiv based on keyword search.
    
    Args:
        keyword: Search term
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary containing paper details or None if no results found
    """
    try:
        search = arxiv.Search(query=keyword, max_results=max_results)
        for result in client.results(search):
            paper = {
                "title": result.title,
                "id": result.entry_id,
                "author": [author.name for author in result.authors],
                "abstract": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d"),
                "doi": result.doi,
                "pdf_url": result.pdf_url,
                "primary_category": result.primary_category,
                "categories": result.categories
            }
            return paper
        return None
    except Exception as e:
        print(f"Error fetching papers: {str(e)}")
        return None

def get_arxiv_paper_by_id(id: str) -> Optional[Dict]:
    """
    Fetch specific paper from Arxiv using its ID.
    
    Args:
        id: Arxiv paper ID
    
    Returns:
        Dictionary containing paper details or None if paper not found
    """
    try:
        search_by_id = arxiv.Search(id_list=[id])
        result = next(client.results(search_by_id), None)
        if not result:
            return None
            
        paper = {
            "title": result.title,
            "id": result.entry_id,
            "author": [author.name for author in result.authors],
            "abstract": result.summary,
            "published": result.published.strftime("%Y-%m-%d"),
            "updated": result.updated.strftime("%Y-%m-%d"),
            "doi": result.doi,
            "pdf_url": result.pdf_url,
            "primary_category": result.primary_category,
            "categories": result.categories
        }
        return paper
    except Exception as e:
        print(f"Error fetching paper: {str(e)}")
        return None

paper = get_arxiv_papers_by_keyword("quantum computing", max_results=1)
print(json.dumps(paper, indent=2))
