from flask import Flask, render_template, request, jsonify, session
from api_client import ScholarAPIClient
import logging
import os
import time  # Add this import
from hive import search_semantic_scholar
from ai_features import AIFeatures

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api_client = ScholarAPIClient()
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "research_hive_secret_key")

# Initialize AI features with the provided API key
api_key = "#"
os.environ["GROQ_API_KEY"] = api_key
ai = AIFeatures(api_key=api_key)

# Log that the API key is set
logger.info("Groq API key set and AI features initialized")


@app.route("/")
def home():
    # Pass AI availability to template
    return render_template("index.html", ai_available=ai.is_available())


@app.route("/search", methods=["POST"])
def search():
    """Handle paper search requests."""
    logger.info("Received search request")

    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("No data provided in request")
            return jsonify(
                {"success": False, "error": "Please provide search parameters"}
            )

        # Extract and validate keywords
        keywords = data.get("keywords", "").strip()
        max_results = min(
            max(int(data.get("max_results", 10)), 1), 20
        )  # Ensure between 1 and 20
        enable_ai = data.get("enable_ai", True)  # Default to True

        if not keywords:
            logger.warning("No keywords provided")
            return jsonify(
                {"success": False, "error": "Please enter keywords to search"}
            )

        # Check if API middleware is available
        if not api_client.health_check():
            logger.warning(
                "Middleware API not available, falling back to direct search"
            )
            # Fall back to direct search if middleware is not available
            result = search_semantic_scholar(keywords, max_results, enable_ai=enable_ai)
        else:
            # Use middleware API for faster search
            logger.info("Using middleware API for search")
            start_time = time.time()
            papers = api_client.search_papers(keywords, max_results)
            search_time = time.time() - start_time
            logger.info(f"Middleware search completed in {search_time:.2f} seconds")

            # If AI is enabled and papers were found, enhance them
            if enable_ai and ai.is_available() and papers:
                logger.info("Enhancing papers with AI features")
                # Process papers with AI features
                for paper in papers:
                    if (
                        paper.get("abstract")
                        and paper["abstract"] != "No abstract available."
                    ):
                        # Add AI-generated summary
                        summary = ai.summarize_paper(paper["abstract"])
                        if summary:
                            paper["ai_summary"] = summary

                        # Add research questions
                        questions = ai.generate_research_questions(
                            paper["abstract"], num_questions=2
                        )
                        if questions:
                            paper["ai_questions"] = questions

                # Generate related topics if we have papers
                if papers:
                    paper_titles = [paper["title"] for paper in papers]
                    related_topics = ai.recommend_related_topics(keywords, paper_titles)

                    if related_topics:
                        result = {"papers": papers, "related_topics": related_topics}
                    else:
                        result = {"papers": papers}
                else:
                    result = papers
            else:
                result = papers

        # Check results
        if result:
            # Handle both formats of results (list or dict with 'papers' key)
            if isinstance(result, dict) and "papers" in result:
                papers = result["papers"]
                related_topics = result.get("related_topics", [])
                logger.info(
                    f"Found {len(papers)} papers and {len(related_topics)} related topics"
                )

                # Store papers in session for other AI features
                session["last_search_papers"] = papers
                session["last_search_field"] = keywords

                return jsonify(
                    {
                        "success": True,
                        "papers": papers,
                        "related_topics": related_topics,
                        "ai_enhanced": True,
                    }
                )
            elif isinstance(result, list):
                papers = result
                logger.info(f"Found {len(papers)} papers")

                # Store papers in session for other AI features
                session["last_search_papers"] = papers
                session["last_search_field"] = keywords

                return jsonify(
                    {"success": True, "papers": papers, "ai_enhanced": False}
                )
            else:
                logger.warning("Unexpected result format")
                return jsonify(
                    {"success": False, "error": "Unexpected result format from search"}
                )
        else:
            logger.warning("No papers found")
            return jsonify(
                {
                    "success": False,
                    "error": f'No papers found matching "{keywords}". Try different keywords.',
                }
            )

    except ValueError as e:
        logger.error(f"Value error in search: {str(e)}")
        return jsonify(
            {"success": False, "error": "Invalid search parameters. Please try again."}
        )
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return jsonify(
            {
                "success": False,
                "error": "An error occurred while searching. Please try again.",
            }
        )


@app.route("/api/ai-status", methods=["GET"])
def ai_status():
    """Check if AI features are available."""
    return jsonify({"available": ai.is_available()})


@app.route("/api/set-api-key", methods=["POST"])
def set_api_key():
    """Set the Groq API key."""
    try:
        data = request.get_json()
        if not data or "api_key" not in data:
            return jsonify({"success": False, "error": "No API key provided"})

        api_key = data["api_key"].strip()
        if not api_key:
            return jsonify({"success": False, "error": "API key cannot be empty"})

        # Set environment variable
        os.environ["GROQ_API_KEY"] = api_key

        # Reinitialize AI features
        global ai
        ai = AIFeatures(api_key=api_key)

        return jsonify({"success": True, "available": ai.is_available()})
    except Exception as e:
        logger.error(f"Error setting API key: {str(e)}")
        return jsonify(
            {"success": False, "error": "An error occurred while setting the API key"}
        )


@app.route("/api/research-gaps", methods=["POST"])
def research_gaps():
    """Find research gaps in the current field based on the papers found."""
    try:
        data = request.get_json()

        # Get papers from session or request
        papers = (
            data.get("papers")
            if data and "papers" in data
            else session.get("last_search_papers")
        )
        field = (
            data.get("field")
            if data and "field" in data
            else session.get("last_search_field", "this research area")
        )

        if not papers or len(papers) < 3:
            return jsonify(
                {
                    "success": False,
                    "error": "Not enough papers to analyze. Please search for more papers first.",
                }
            )

        logger.info(
            f"Finding research gaps in field: {field} with {len(papers)} papers"
        )

        # Analyze research gaps
        gaps_analysis = ai.find_research_gaps(papers, field)

        if not gaps_analysis:
            return jsonify(
                {
                    "success": False,
                    "error": "Unable to analyze research gaps. Please try again.",
                }
            )

        return jsonify(
            {
                "success": True,
                "research_gaps": gaps_analysis.get("research_gaps", []),
                "emerging_trends": gaps_analysis.get("emerging_trends", []),
                "research_opportunities": gaps_analysis.get(
                    "research_opportunities", []
                ),
            }
        )

    except Exception as e:
        logger.error(f"Error finding research gaps: {str(e)}")
        return jsonify(
            {
                "success": False,
                "error": "An error occurred while analyzing research gaps.",
            }
        )


@app.route("/api/chat", methods=["POST"])
def chat():
    """Answer questions about papers or research fields."""
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"success": False, "error": "No question provided"})

        question = data.get("question").strip()
        if not question:
            return jsonify({"success": False, "error": "Question cannot be empty"})

        # Determine if we should use papers or answer a general question
        use_papers = data.get("use_papers", True)
        papers = (
            data.get("papers")
            if data and "papers" in data
            else session.get("last_search_papers")
        )
        field = (
            data.get("field")
            if data and "field" in data
            else session.get("last_search_field")
        )

        logger.info(f"Answering question: {question}")

        if use_papers and papers and len(papers) > 0:
            # Answer based on papers
            answer = ai.chat_with_papers(question, papers)
        else:
            # Answer general research question
            answer = ai.answer_general_research_question(question, field)

        if not answer:
            return jsonify(
                {
                    "success": False,
                    "error": "Unable to generate an answer. Please try again.",
                }
            )

        return jsonify({"success": True, "answer": answer})

    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return jsonify(
            {
                "success": False,
                "error": "An error occurred while answering your question.",
            }
        )


@app.route("/chat")
def chat_page():
    """Render the chat interface page."""
    return render_template("chat.html", ai_available=ai.is_available())


@app.route("/research-gaps")
def research_gaps_page():
    """Render the research gaps analysis page."""
    return render_template("research_gaps.html", ai_available=ai.is_available())


if __name__ == "__main__":
    app.run(debug=True)
