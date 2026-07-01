import streamlit as st
from semanticscholar import SemanticScholar

# Cache API results to speed up repeated searches
@st.cache_data(ttl=300)  # Cache for 5 minutes
def search_semantic_scholar(keywords, max_results=5):
    """Searches Semantic Scholar for papers related to the given keywords."""
    sch = SemanticScholar()
    query = " ".join(keywords)
    
    try:
        results = sch.search_paper(query, limit=max_results)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

    if not results:
        return []

    papers = [
        {
            "title": paper.title,
            "authors": ", ".join([author["name"] for author in paper.authors]),
            "year": paper.year if paper.year else "Unknown",
            "url": paper.url,
        }
        for paper in results
    ]
    return papers

# UI Setup
st.set_page_config(page_title="Research Hive", layout="wide")
st.title("🚀 Research Hive - Find Research Papers Fast")
st.markdown("Enter keywords to search for academic papers.")

# Keyword Input
keywords = st.text_input("🔍 Enter Keywords:", "").strip()
max_results = st.slider("📄 Number of Articles:", min_value=1, max_value=20, value=5)

# Search Button
if st.button("Search 🔎"):
    if keywords:
        keywords_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]

        with st.spinner("🔄 Searching... Please wait."):
            papers = search_semantic_scholar(keywords_list, max_results)

        if papers:
            for paper in papers:
                st.subheader(paper["title"])
                st.write(f"👨‍🔬 **Authors:** {paper['authors']}")
                st.write(f"📅 **Year:** {paper['year']}")
                st.markdown(f"[📖 Read Paper]({paper['url']})")
                st.divider()
        else:
            st.warning("⚠️ No papers found. Try different keywords.")
    else:
        st.error("❌ Please enter at least one keyword.")

# Improved Button Styles
st.markdown("""
    <style>
        .stButton button {
            background-color: #1f77b4;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton button:hover {
            background-color: #10537c;
        }
    </style>
""", unsafe_allow_html=True)
