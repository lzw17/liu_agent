"""Web search service with multiple search engines."""
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from duckduckgo_search import DDGS
from googlesearch import search as google_search
from bs4 import BeautifulSoup
from ..core import get_config, logger
from ..models.schemas import SearchResult


class SearchEngine:
    """Base class for search engines."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Perform search and return results."""
        raise NotImplementedError


class DuckDuckGoEngine(SearchEngine):
    """DuckDuckGo search engine."""
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using DuckDuckGo."""
        try:
            results = []
            
            # Use asyncio to run the synchronous DDGS in a thread
            def _search():
                with DDGS() as ddgs:
                    return list(ddgs.text(
                        query, 
                        max_results=max_results,
                        region=self.config.get("region", "cn"),
                        safesearch="moderate"
                    ))
            
            search_results = await asyncio.get_event_loop().run_in_executor(
                None, _search
            )
            
            for result in search_results:
                results.append(SearchResult(
                    title=result.get("title", ""),
                    url=result.get("href", ""),
                    snippet=result.get("body", ""),
                    source="duckduckgo"
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []


class GoogleEngine(SearchEngine):
    """Google search engine."""
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Google."""
        try:
            results = []
            
            # Check if we have Google API credentials
            google_config = self.config.get("google", {})
            api_key = google_config.get("api_key")
            search_engine_id = google_config.get("search_engine_id")
            
            if api_key and search_engine_id:
                # Use Google Custom Search API
                results = await self._search_with_api(query, max_results, api_key, search_engine_id)
            else:
                # Use googlesearch-python library (less reliable)
                results = await self._search_with_library(query, max_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []
    
    async def _search_with_api(
        self, 
        query: str, 
        max_results: int, 
        api_key: str, 
        search_engine_id: str
    ) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        try:
            async with httpx.AsyncClient() as client:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": api_key,
                    "cx": search_engine_id,
                    "q": query,
                    "num": min(max_results, 10)  # API limit is 10 per request
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for item in data.get("items", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source="google"
                    ))
                
                return results
                
        except Exception as e:
            logger.error(f"Google API search failed: {e}")
            return []
    
    async def _search_with_library(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using googlesearch-python library."""
        try:
            def _search():
                return list(google_search(
                    query, 
                    num_results=max_results,
                    lang=self.config.get("language", "zh-CN")
                ))
            
            urls = await asyncio.get_event_loop().run_in_executor(
                None, _search
            )
            
            results = []
            for url in urls:
                # Try to get title and snippet by fetching the page
                title, snippet = await self._get_page_info(url)
                results.append(SearchResult(
                    title=title or url,
                    url=url,
                    snippet=snippet or "",
                    source="google"
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Google library search failed: {e}")
            return []
    
    async def _get_page_info(self, url: str) -> tuple[str, str]:
        """Get title and snippet from a webpage."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get title
                title_tag = soup.find('title')
                title = title_tag.text.strip() if title_tag else ""
                
                # Get description from meta tag
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                snippet = desc_tag.get('content', '') if desc_tag else ""
                
                # If no description, get first paragraph
                if not snippet:
                    p_tag = soup.find('p')
                    snippet = p_tag.text.strip()[:200] if p_tag else ""
                
                return title, snippet
                
        except Exception:
            return "", ""


class BingEngine(SearchEngine):
    """Bing search engine (placeholder)."""
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using Bing (not implemented)."""
        logger.warning("Bing search not implemented")
        return []


class SearchService:
    """Service for managing web searches across multiple engines."""
    
    def __init__(self):
        self.config = get_config()
        self.engines = self._initialize_engines()
    
    def _initialize_engines(self) -> Dict[str, SearchEngine]:
        """Initialize search engines."""
        engines = {}
        search_config = self.config.search.model_dump()
        
        engines["duckduckgo"] = DuckDuckGoEngine(search_config)
        engines["google"] = GoogleEngine(search_config)
        engines["bing"] = BingEngine(search_config)
        
        return engines
    
    async def search(
        self, 
        query: str, 
        max_results: int = 10, 
        engine: Optional[str] = None
    ) -> List[SearchResult]:
        """Perform web search using specified or default engine."""
        if engine is None:
            engine = self.config.search.primary_engine
        
        # Try primary engine
        if engine in self.engines:
            results = await self.engines[engine].search(query, max_results)
            if results:
                logger.info(f"Search successful with {engine}: {len(results)} results")
                return results
            else:
                logger.warning(f"No results from {engine}, trying fallback engines")
        
        # Try fallback engines
        for fallback_engine in self.config.search.fallback_engines:
            if fallback_engine != engine and fallback_engine in self.engines:
                try:
                    results = await self.engines[fallback_engine].search(query, max_results)
                    if results:
                        logger.info(f"Search successful with fallback {fallback_engine}: {len(results)} results")
                        return results
                except Exception as e:
                    logger.warning(f"Fallback engine {fallback_engine} failed: {e}")
                    continue
        
        logger.error(f"All search engines failed for query: {query}")
        return []
    
    async def search_and_summarize(
        self, 
        query: str, 
        max_results: int = 5
    ) -> Dict[str, Any]:
        """Search and return results with summary."""
        results = await self.search(query, max_results)
        
        if not results:
            return {
                "results": [],
                "summary": "No search results found.",
                "total_results": 0
            }
        
        # Create a summary of the search results
        summary_parts = []
        for i, result in enumerate(results[:3], 1):  # Summarize top 3 results
            summary_parts.append(f"{i}. {result.title}: {result.snippet[:100]}...")
        
        summary = "Top search results:\n" + "\n".join(summary_parts)
        
        return {
            "results": results,
            "summary": summary,
            "total_results": len(results)
        }
    
    def get_available_engines(self) -> List[str]:
        """Get list of available search engines."""
        return list(self.engines.keys())


# Global search service instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get the global search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
