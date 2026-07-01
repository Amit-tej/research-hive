from flask import Flask, request, jsonify
from api_service import ScholarAPIService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api_service = ScholarAPIService()

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Research Hive API is running",
        "endpoints": [
            "/api/search?query=your_query&limit=10",
            "/api/health"
        ]
    })

@app.route('/api/search', methods=['GET'])
def search_papers():
    query = request.args.get('query', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    if limit < 1 or limit > 50:
        return jsonify({"error": "Limit must be between 1 and 50"}), 400
    
    papers = api_service.search_papers(query, limit)
    return jsonify({"results": papers, "count": len(papers)})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    logger.info("Starting API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)