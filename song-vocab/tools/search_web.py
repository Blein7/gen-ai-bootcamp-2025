from duckduckgo_search import DDGS
from typing import List, Dict
import json
import traceback
import time

def search_web(query: str) -> List[Dict[str, str]]:
    """
    Search for song lyrics using DuckDuckGo
    
    Args:
        query: Search query
        
    Returns:
        List of search results with titles and URLs
    """
    try:
        # Add 'lyrics' to the query to focus on lyrics pages
        search_query = f"{query} lyrics"
        print(f"[search_web] Searching for: {search_query}")
        
        # Common lyrics sites
        lyrics_sites = [
            "genius.com",
            "azlyrics.com",
            "lyrics.com",
            "musixmatch.com"
        ]
        
        # Initialize results
        results = []
        seen_urls = set()
        
        # Try general search first
        try:
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(search_query, max_results=10))
            
            # Process results
            for r in ddg_results:
                url = r.get('link', '') or r.get('href', '')
                if url and url not in seen_urls:
                    results.append({
                        'title': r.get('title', ''),
                        'url': url,
                        'source': 'search'
                    })
                    seen_urls.add(url)
            
        except Exception as e:
            print(f"[search_web] Error in general search: {str(e)}")
        
        # Log results
        print(f"[search_web] Found {len(results)} total results")
        for r in results[:3]:
            print(f"[search_web] - {r['url']}")
            
        return results
        
    except Exception as e:
        print(f"[search_web] Error: {str(e)}")
        return []