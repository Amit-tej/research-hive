from semanticscholar import SemanticScholar
import logging
import time
from ai_features import AIFeatures
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI features with API key
ai = AIFeatures(api_key=os.environ.get("GROQ_API_KEY"))

def search_semantic_scholar(keywords, max_results=10, enable_ai=True):
    """
    Searches Semantic Scholar for papers related to the given keywords.
    Returns papers sorted by relevance with essential fields: title, authors, year, abstract, and URL.
    If enable_ai is True and API key is available, enhances results with AI features.
    """
    try:
        # Initialize API
        sch = SemanticScholar()
        logger.info("Initialized Semantic Scholar API")
        
        # Clean up query
        query = str(keywords).strip()
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
                results = sch.search_paper(query, limit=max_results)
                
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
        paper_titles = []  # Collect titles for related topics recommendation
        
        for i, paper in enumerate(results):
            try:
                if not paper.title:
                    logger.debug(f"Skipping paper {i+1}: No title")
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

                # Get abstract
                abstract = getattr(paper, 'abstract', 'No abstract available.').strip()
                
                # Create paper entry
                paper_entry = {
                    'title': paper.title.strip(),
                    'authors': ', '.join(authors) if authors else 'Unknown Authors',
                    'year': getattr(paper, 'year', 'Unknown'),
                    'url': getattr(paper, 'url', '') or f'https://www.semanticscholar.org/paper/{getattr(paper, "paperId", "")}',
                    'abstract': abstract
                }
                
                # Add AI enhancements if enabled and available
                if enable_ai and ai.is_available() and abstract and abstract != 'No abstract available.':
                    logger.info(f"Enhancing paper {i+1} with AI features")
                    
                    # Add AI-generated summary
                    summary = ai.summarize_paper(abstract)
                    if summary:
                        paper_entry['ai_summary'] = summary
                    
                    # Add research questions
                    questions = ai.generate_research_questions(abstract, num_questions=2)
                    if questions:
                        paper_entry['ai_questions'] = questions
                    
                    # Add impact analysis
                    impact = ai.analyze_paper_impact(paper_entry['title'], abstract, paper_entry['year'])
                    if impact:
                        paper_entry['ai_impact'] = impact
                    
                    # Add technical term explanations
                    terms = ai.explain_technical_terms(abstract, max_terms=3)
                    if terms:
                        paper_entry['ai_terms'] = terms
                
                processed_papers.append(paper_entry)
                paper_titles.append(paper_entry['title'])
                logger.info(f"Processed paper {i+1}: {paper_entry['title'][:50]}...")

            except Exception as e:
                logger.error(f"Error processing paper {i+1}: {str(e)}")
                continue

            if len(processed_papers) >= max_results:
                logger.info(f"Reached maximum results limit of {max_results}")
                break

        # Add related topics recommendations if AI is available
        if enable_ai and ai.is_available() and processed_papers:
            related_topics = ai.recommend_related_topics(query, paper_titles)
            if related_topics:
                # Add as a separate field in the response
                return {
                    'papers': processed_papers,
                    'related_topics': related_topics
                }

        logger.info(f"Successfully processed {len(processed_papers)} papers")
        
        # Return just the papers if no AI enhancements for related topics
        if enable_ai and ai.is_available():
            return {'papers': processed_papers}
        else:
            return processed_papers

    except Exception as e:
        logger.error(f"Search failed with error: {str(e)}")
        return []

if __name__ == "__main__":
    print("\nResearch Paper Search")
    print("=" * 50)
    
    query = input("\nEnter search query: ").strip()
    if not query:
        print("Error: Please enter a search query")
    else:
        try:
            max_results = int(input("Number of papers to find (1-20): ").strip())
            if max_results < 1 or max_results > 20:
                print("Error: Please enter a number between 1 and 20")
            else:
                papers = search_semantic_scholar(query, max_results)
                if papers:
                    print(f"\nFound {len(papers)} relevant papers:\n")
                    for i, paper in enumerate(papers, 1):
                        print(f"{i}. {paper['title']}")
                        print(f"   Authors: {paper['authors']}")
                        print(f"   Year: {paper['year']}")
                        print(f"   URL: {paper['url']}")
                        if paper['abstract']:
                            print(f"   Abstract: {paper['abstract'][:300]}...")
                        print("-" * 50)
                else:
                    print("\nNo papers found matching your query. Try different keywords.")
        except ValueError as e:
            print(f"Error: {str(e)}")