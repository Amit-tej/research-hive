# Research Hive - AI-Enhanced Research Platform

Research Hive is a comprehensive web application that helps users find, understand, and explore academic research papers. It combines the Semantic Scholar API for paper search with Groq's AI capabilities to provide advanced features like paper summaries, research gap analysis, and an interactive research assistant.

## Features

### Basic Features

- Search for academic papers using keywords
- View paper details including title, authors, year, and abstract
- Access the full paper via direct links

### AI-Enhanced Features (Requires Groq API Key)

- **AI-Generated Summaries**: Get concise summaries of paper abstracts
- **Research Questions**: AI-generated questions for future research based on the paper
- **Impact Analysis**: Brief analysis of the paper's potential significance and relevance
- **Technical Term Explanations**: Explanations of domain-specific terms found in the abstract
- **Related Research Topics**: Suggestions for related research areas to explore

### Advanced AI Features

- **Research Gap Finder**: Analyze multiple papers to identify under-explored areas and emerging trends in a research field
- **AI Research Assistant**: Interactive chat interface to ask questions about papers or general research concepts

## Setup and Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python app.py
   ```
6. Open your browser and navigate to `http://127.0.0.1:5000`

## Setting Up AI Features

To enable AI features, you need a Groq API key:

1. Sign up for an account at [groq.com](https://console.groq.com/signup)
2. Generate an API key from your account dashboard
3. In the Research Hive application, click on "AI Settings" in the top right corner
4. Enter your API key and click "Save API Key"

You can also set the API key as an environment variable:

```
# Windows
set GROQ_API_KEY=your_api_key_here

# Mac/Linux
export GROQ_API_KEY=your_api_key_here
```

## Usage

### Paper Search

1. Enter keywords in the search box (e.g., "machine learning, neural networks")
2. Set the number of results you want to see (1-20)
3. Toggle the AI features on/off using the switch
4. Click "Search" to find papers
5. Explore the results with AI-enhanced features (if enabled)
6. Click on related topics to start a new search with that topic

### Research Gap Finder

1. Search for papers first to build a collection
2. Navigate to the Research Gaps page
3. Enter or confirm the field of study
4. Click "Analyze Research Gaps"
5. Review the identified research gaps, emerging trends, and research opportunities

### AI Research Assistant

1. Navigate to the Chat page
2. Choose between "Based on Papers" mode (to discuss papers from your search) or "General Knowledge" mode
3. Type your question or select from example questions
4. View the AI's response and continue the conversation

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Paper Data**: Semantic Scholar API
- **AI Features**: Groq API (Llama 3 8B model)
- **Frontend**: HTML, CSS, JavaScript

## License

This project is open source and available under the MIT License.
