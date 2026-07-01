import os
import logging
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIFeatures:
    def __init__(self, api_key=None):
        """Initialize the AI Features with Groq API key."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("No Groq API key provided. AI features will not work.")
            self.client = None
        else:
            logger.info("Initializing Groq client")
            self.client = Groq(api_key=self.api_key)
            
    def is_available(self):
        """Check if the AI service is available."""
        return self.client is not None
    
    def summarize_paper(self, abstract, max_length=150):
        """Generate a concise summary of a paper abstract."""
        if not self.is_available():
            logger.warning("AI service not available for summarization")
            return None
            
        try:
            logger.info("Generating paper summary")
            prompt = f"""Summarize the following research paper abstract in a concise way (maximum {max_length} words):
            
            {abstract}
            
            Provide only the summary without any introductory text.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Using Llama 3 8B model
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that summarizes academic papers concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary of length {len(summary.split())} words")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
    
    def generate_research_questions(self, abstract, num_questions=3):
        """Generate research questions based on a paper abstract."""
        if not self.is_available():
            logger.warning("AI service not available for question generation")
            return []
            
        try:
            logger.info(f"Generating {num_questions} research questions")
            prompt = f"""Based on the following research paper abstract, generate {num_questions} thought-provoking research questions that could guide future research:
            
            {abstract}
            
            Format each question on a new line, starting with a number and a period (e.g., "1. ").
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that generates insightful research questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            questions_text = response.choices[0].message.content.strip()
            
            # Parse the questions into a list
            questions = []
            for line in questions_text.split('\n'):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_questions+2)):
                    # Remove the number prefix and add to list
                    question = line[line.find('.')+1:].strip()
                    questions.append(question)
            
            logger.info(f"Generated {len(questions)} research questions")
            return questions[:num_questions]  # Ensure we return exactly the requested number
            
        except Exception as e:
            logger.error(f"Error generating research questions: {str(e)}")
            return []
    
    def analyze_paper_impact(self, title, abstract, year):
        """Analyze the potential impact and relevance of a research paper."""
        if not self.is_available():
            logger.warning("AI service not available for impact analysis")
            return None
            
        try:
            logger.info("Analyzing paper impact")
            current_year = 2025  # Hardcoded current year
            
            prompt = f"""Analyze the potential impact and relevance of this research paper:
            
            Title: {title}
            Year: {year}
            Abstract: {abstract}
            
            Provide a brief analysis (2-3 sentences) of:
            1. The paper's potential significance to its field
            2. How relevant/applicable the research is today ({current_year})
            
            Format your response as a paragraph without numbering.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful research analyst that evaluates the impact and relevance of academic papers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.4
            )
            
            analysis = response.choices[0].message.content.strip()
            logger.info("Generated paper impact analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing paper impact: {str(e)}")
            return None
    
    def recommend_related_topics(self, keywords, paper_titles, num_topics=5):
        """Recommend related research topics based on search keywords and found papers."""
        if not self.is_available():
            logger.warning("AI service not available for topic recommendations")
            return []
            
        try:
            logger.info(f"Generating {num_topics} related topic recommendations")
            
            # Combine paper titles into a single string
            titles_text = "\n".join([f"- {title}" for title in paper_titles[:5]])  # Limit to first 5 papers
            
            prompt = f"""Based on the following search keywords and research paper titles, suggest {num_topics} related research topics or areas that might be interesting to explore:
            
            Search Keywords: {keywords}
            
            Paper Titles:
            {titles_text}
            
            Provide each topic as a short phrase (3-6 words) on a new line, starting with a bullet point (e.g., "• Topic name").
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that recommends related research topics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.6
            )
            
            topics_text = response.choices[0].message.content.strip()
            
            # Parse the topics into a list
            topics = []
            for line in topics_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    # Remove the bullet point and add to list
                    topic = line[1:].strip()
                    topics.append(topic)
            
            logger.info(f"Generated {len(topics)} topic recommendations")
            return topics[:num_topics]  # Ensure we return exactly the requested number
            
        except Exception as e:
            logger.error(f"Error generating topic recommendations: {str(e)}")
            return []
    
    def explain_technical_terms(self, abstract, max_terms=3):
        """Identify and explain technical terms from a paper abstract."""
        if not self.is_available():
            logger.warning("AI service not available for technical term explanation")
            return {}
            
        try:
            logger.info(f"Identifying and explaining up to {max_terms} technical terms")
            
            prompt = f"""Identify up to {max_terms} technical or domain-specific terms from the following research paper abstract, and provide a brief, clear explanation for each:
            
            {abstract}
            
            Format your response as a JSON-like structure with term as key and explanation as value:
            
            term1: explanation1
            term2: explanation2
            term3: explanation3
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that explains technical terms in simple language."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.3
            )
            
            explanations_text = response.choices[0].message.content.strip()
            
            # Parse the explanations into a dictionary
            explanations = {}
            for line in explanations_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':', 1)
                    term = parts[0].strip()
                    explanation = parts[1].strip()
                    explanations[term] = explanation
            
            logger.info(f"Explained {len(explanations)} technical terms")
            return explanations
            
        except Exception as e:
            logger.error(f"Error explaining technical terms: {str(e)}")
            return {}
    
    def find_research_gaps(self, papers, field_name):
        """
        Analyze multiple papers to identify research gaps and emerging areas.
        
        Args:
            papers: List of paper dictionaries with title, abstract, and year
            field_name: Name of the research field or topic
            
        Returns:
            Dictionary with research gaps, emerging areas, and recommendations
        """
        if not self.is_available():
            logger.warning("AI service not available for research gap analysis")
            return None
            
        try:
            logger.info(f"Analyzing research gaps in {field_name} field")
            
            # Prepare paper data for analysis
            paper_data = []
            for i, paper in enumerate(papers[:8]):  # Limit to 8 papers to avoid token limits
                paper_data.append(f"Paper {i+1}:\nTitle: {paper['title']}\nYear: {paper['year']}\nAbstract: {paper['abstract'][:500]}...\n")
            
            papers_text = "\n".join(paper_data)
            
            prompt = f"""Analyze the following research papers in the field of {field_name} to identify:
            
            1. Research Gaps: Areas that seem under-explored or have unanswered questions
            2. Emerging Trends: New directions or methodologies that are gaining traction
            3. Potential Research Opportunities: Specific research questions or projects that could address the gaps
            
            Papers:
            {papers_text}
            
            Format your response as follows:
            
            RESEARCH GAPS:
            - [Gap 1]
            - [Gap 2]
            - [Gap 3]
            
            EMERGING TRENDS:
            - [Trend 1]
            - [Trend 2]
            - [Trend 3]
            
            RESEARCH OPPORTUNITIES:
            - [Opportunity 1]
            - [Opportunity 2]
            - [Opportunity 3]
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a research analyst specializing in identifying research gaps and opportunities in academic literature."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse the analysis into sections
            sections = {
                "research_gaps": [],
                "emerging_trends": [],
                "research_opportunities": []
            }
            
            current_section = None
            
            for line in analysis_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if "RESEARCH GAPS:" in line.upper():
                    current_section = "research_gaps"
                elif "EMERGING TRENDS:" in line.upper():
                    current_section = "emerging_trends"
                elif "RESEARCH OPPORTUNITIES:" in line.upper():
                    current_section = "research_opportunities"
                elif current_section and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                    item = line[1:].strip()
                    if item and current_section in sections:
                        sections[current_section].append(item)
            
            logger.info(f"Identified {len(sections['research_gaps'])} research gaps, {len(sections['emerging_trends'])} emerging trends, and {len(sections['research_opportunities'])} research opportunities")
            return sections
            
        except Exception as e:
            logger.error(f"Error finding research gaps: {str(e)}")
            return None
    
    def chat_with_papers(self, question, papers, max_papers=3):
        """
        Answer questions about papers or research fields based on provided papers.
        
        Args:
            question: User's question about papers or research field
            papers: List of paper dictionaries with title, abstract, and year
            max_papers: Maximum number of papers to include in context
            
        Returns:
            AI-generated answer to the question
        """
        if not self.is_available():
            logger.warning("AI service not available for paper chat")
            return None
            
        try:
            logger.info(f"Answering question about papers: {question}")
            
            # Prepare paper data for context
            paper_data = []
            for i, paper in enumerate(papers[:max_papers]):  # Limit papers to avoid token limits
                paper_data.append(f"Paper {i+1}:\nTitle: {paper['title']}\nAuthors: {paper['authors']}\nYear: {paper['year']}\nAbstract: {paper['abstract']}\n")
            
            papers_text = "\n".join(paper_data)
            
            prompt = f"""Based on the following research papers, please answer this question concisely:
            
            Question: {question}
            
            Papers:
            {papers_text}
            
            Provide a concise answer based on the information in these papers. If the papers don't contain enough information to fully answer the question, acknowledge this limitation and provide the best possible answer with the available information.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable research assistant who helps users understand academic papers and research fields. You provide accurate, concise, and helpful answers based on the papers provided to you."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.4
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer of length {len(answer.split())} words")
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question about papers: {str(e)}")
            return None
    
    def answer_general_research_question(self, question, field=None):
        """
        Answer general questions about research methods, fields, or concepts.
        
        Args:
            question: User's question about research
            field: Optional field or context to frame the answer
            
        Returns:
            AI-generated answer to the question
        """
        if not self.is_available():
            logger.warning("AI service not available for general research questions")
            return None
            
        try:
            logger.info(f"Answering general research question: {question}")
            
            field_context = f" in the field of {field}" if field else ""
            
            prompt = f"""Please answer the following research-related question{field_context}:
            
            Question: {question}
            
            Provide a comprehensive, educational answer that would be helpful to a researcher or student. Include relevant examples or methodologies where appropriate.
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable research assistant who helps users understand research methods, concepts, and fields. You provide accurate, educational answers to research-related questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer of length {len(answer.split())} words")
            return answer
            
        except Exception as e:
            logger.error(f"Error answering general research question: {str(e)}")
            return None