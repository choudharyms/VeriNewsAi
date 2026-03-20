import re
import hashlib

# Sensationalist keywords for fallback scoring
SENSATIONAL_KEYWORDS = [
    "shocking", "breaking", "viral", "unbelievable", "exposed", 
    "must see", "miracle", "secret", "hoax", "conspiracy",
    "exclusive", "mind-blowing", "scandal", "hidden truth"
]

def clean_text(text: str, max_length: int = 3000) -> str:
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate
    return text[:max_length]

def get_keyword_score(text: str) -> int:
    """
    Returns a suspicion score (0-100) based on sensationalist keywords.
    """
    if not text:
        return 0
        
    text_lower = text.lower()
    matches = [word for word in SENSATIONAL_KEYWORDS if word in text_lower]
    
    # Simple linear scoring: each keyword adds 20 points, capped at 100
    score = min(len(matches) * 20, 100)
    return score

def get_cache_key(text: str) -> str:
    """
    Generates a hash-based cache key for given text.
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()
