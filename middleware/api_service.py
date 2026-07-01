from semanticscholar import SemanticScholar
import os
import json
import time
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("c:/Users/bharg/Downloads/Research Hive/cache")

class ScholarAPIService:
    def __init__(self):
        # Create cache directory if it doesn't exist
        os.makedirs(CACHE_DIR, exist_ok=True)
        self._clean_old_cache()
    
    def _clean_old_cache(self):
        """Remove cache files older than 7 days"""
        try:
            now = time.time()
            for cache_file in CACHE_DIR.glob("*.json"):
                file_time = cache_file.stat().st_mtime
                if now - file_time > 7 * 24 * 60 * 60:  # 7 days
                    os.remove(cache_file)
                    logger.info(f"Removed old cache file: {cache_file.name}")
        except Exception as e:
            logger.error(f"Error cleaning cache: {str(e)}")
    
    def _get_cache_key(self, query, limit):
        """Generate a cache key from the query and limit"""
        # Create a safe filename from the query
        safe_query = "".join(c if c.isalnum() else "_" for c in query)
        return f"{safe_query}_{limit}.json"
    
    def _get_from_cache(self, query, limit):
        """Try to get results from cache"""
        cache_key = self._get_cache_key(query, limit)
        cache_path = CACHE_DIR / cache_key
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Cache hit for query: '{query}'")
                    return data
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
        
        return None
    
    def _save_to_cache(self, query, limit, data):
        """Save results to cache"""
        cache_key = self._get_cache_key(query, limit)
        cache_path = CACHE_DIR / cache_key
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            logger.info(f"Saved to cache: '{query}'")
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
    
    def search_papers(self, query, limit=10):
        """Search for papers with caching"""
        # Check cache first
        cached_results = self._get_from_cache(query, limit)
        if cached_results:
            return cached_results
        
        # If not in cache, fetch from API
        try:
            # Initialize API
            sch = SemanticScholar()
            logger.info("Initialized Semantic Scholar API")
            
            # Clean up query
            query = str(query).strip()
            query = " ".join(query.replace(",", " ").split())
            logger.info(f"Cleaned query: '{query}'")

            if not query:
                logger.warning("Empty query")
                return []

            # Search with retry
            max_retries = 3
            results = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Search attempt {attempt + 1}/{max_retries}")
                    results = sch.search_paper(query, limit=limit)
                    
                    if results:
                        logger.info(f"Search successful, found {len(results)} results")
                        break
                    else:
                        logger.warning("Search returned no results")
                        
                except Exception as e:
                    logger.error(f"Search attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    logger.info("Waiting before retry...")
                    time.sleep(1)
            
            if not results:
                logger.warning("No results found after all attempts")
                return []

            # Process results
            processed_papers = []
            for paper in results:
                try:
                    if not paper.title:
                        continue

                    # Extract authors
                    authors = []
                    if hasattr(paper, 'authors') and paper.authors:
                        for author in paper.authors:
                            try:
                                if isinstance(author, dict) and 'name' in author:
                                    authors.append(author['name'])
                                elif hasattr(author, 'name'):
                                    authors.append(author.name)
                                elif isinstance(author, str):
                                    authors.append(author)
                            except Exception as e:
                                logger.warning(f"Error processing author: {str(e)}")

                    # Create paper entry
                    paper_entry = {
                        'title': paper.title.strip(),
                        'authors': ', '.join(authors) if authors else 'Unknown Authors',
                        'year': getattr(paper, 'year', 'Unknown'),
                        'url': getattr(paper, 'url', '') or f'https://www.semanticscholar.org/paper/{getattr(paper, "paperId", "")}',
                        'abstract': getattr(paper, 'abstract', 'No abstract available.').strip()
                    }
                    
                    processed_papers.append(paper_entry)

                except Exception as e:
                    logger.error(f"Error processing paper: {str(e)}")
                    continue

            # Save to cache
            if processed_papers:
                self._save_to_cache(query, limit, processed_papers)
            
            return processed_papers

        except Exception as e:
            logger.error(f"Search failed with error: {str(e)}")
            return []