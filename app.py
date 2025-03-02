from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

CDP_DOCS = {
    "segment": "https://segment.com/docs/",
    "mparticle": "https://docs.mparticle.com/",
    "lytics": "https://docs.lytics.com/",
    "zeotap": "https://docs.zeotap.com/home/en-us/"
}

def fetch_documentation(cdp):
    """Fetches and scrapes documentation content from the given CDP."""
    url = CDP_DOCS.get(cdp.lower())
    if not url:
        return "CDP not found."
    
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to retrieve documentation."
    
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join([p.text for p in soup.find_all('p')])
    return text[:2000]  # Limit text to avoid excessive data transfer

def search_documentation(cdp, query):
    """Searches the documentation for relevant answers."""
    text = fetch_documentation(cdp)
    
    if "not found" in text.lower() or "failed" in text.lower():
        return text
    
    # Find relevant sections
    match = re.search(query, text, re.IGNORECASE)
    if match:
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 300)
        return text[start:end] + "..."
    
    return "No relevant information found. Please check the official documentation."

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    cdp = data.get("cdp")
    query = data.get("query")
    
    if not cdp or not query:
        return jsonify({"error": "CDP and query are required."}), 400
    
    answer = search_documentation(cdp, query)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
