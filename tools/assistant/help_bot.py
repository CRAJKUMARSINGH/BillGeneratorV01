import json
from difflib import get_close_matches
from pathlib import Path

# Load FAQ data
FAQ_FILE = Path(__file__).parent / "faq.json"

def load_faq():
    """Load FAQ data from JSON file"""
    try:
        if FAQ_FILE.exists():
            with open(FAQ_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return default FAQ if file doesn't exist
            return {
                "how to generate pdf": "Go to 'Output → PDF', choose statutory format, click Generate.",
                "xml validation failed": "Ensure XML conforms to government schema under /schemas/latest.xsd.",
                "csv format error": "Check that all required columns exist in your input file.",
                "file not found": "Verify the file path and ensure the file exists.",
                "memory error": "Try processing smaller batches of files.",
                "slow performance": "Close other applications and ensure sufficient RAM is available."
            }
    except Exception:
        # Return empty dict if there's an error loading the file
        return {}

FAQ = load_faq()

def get_answer(query):
    """
    Get an answer for a query using fuzzy matching.
    
    Args:
        query (str): User's question
        
    Returns:
        str: Answer to the question or default message
    """
    if not query:
        return "Please enter a question."
    
    # Convert query to lowercase for matching
    query_lower = query.lower()
    
    # Try exact match first
    if query_lower in FAQ:
        return FAQ[query_lower]
    
    # Try fuzzy matching
    matches = get_close_matches(query_lower, FAQ.keys(), n=1, cutoff=0.5)
    if matches:
        return FAQ[matches[0]]
    
    return "I couldn't find an answer to your question. Please refer to the user manual or contact support."

def add_faq_entry(question, answer):
    """
    Add a new FAQ entry.
    
    Args:
        question (str): The question
        answer (str): The answer
    """
    FAQ[question.lower()] = answer
    try:
        with open(FAQ_FILE, 'w', encoding='utf-8') as f:
            json.dump(FAQ, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving FAQ: {e}")

# Create default FAQ file if it doesn't exist
if not FAQ_FILE.exists():
    try:
        with open(FAQ_FILE, 'w', encoding='utf-8') as f:
            json.dump(FAQ, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error creating FAQ file: {e}")