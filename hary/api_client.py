import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScholarAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if the API server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API health check failed: {str(e)}")
            return False
    
    def search_papers(self, query, limit=10, max_retries=3):
        """Search for papers using the middleware API"""
        if not query:
            logger.warning("Empty query")
            return []
        
        # Clean up query
        query = str(query).strip()
        query = " ".join(query.replace(",", " ").split())
        
        # Retry logic
        for attempt in range(max_retries):
            try:
                logger.info(f"API request attempt {attempt + 1}/{max_retries}")
                
                response = self.session.get(
                    f"{self.base_url}/api/search",
                    params={"query": query, "limit": limit},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"API request successful, found {data.get('count', 0)} results")
                    return data.get("results", [])
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"API request failed: {str(e)}")
                
            # Wait before retry
            if attempt < max_retries - 1:
                logger.info(f"Waiting before retry...")
                time.sleep(2)
        
        logger.error("All API request attempts failed")
        return []