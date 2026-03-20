from newspaper import Article
from utils.logger import logger
import httpx

def extract_article(url: str) -> str:
    """
    Extracts clean text from a given URL using newspaper3k.
    """
    try:
        logger.info("Starting article extraction", url=url)
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        # Use simple requests with timeout
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=10, allow_redirects=True)
        logger.info("Download attempt complete", url=url, status_code=res.status_code, length=len(res.text))
        
        if res.status_code != 200:
            return ""
            
        html = res.text

        # Now parse the HTML with newspaper
        article = Article(url)
        article.set_html(html)
        article.parse()
        
        if not article.text:
            logger.warning("No text extracted from HTML", url=url, html_length=len(html))
            return ""
            
        logger.info("Article extraction successful", url=url, text_length=len(article.text))
        return article.text
        
    except Exception as e:
        logger.error("Article extraction failed", url=url, error=str(e))
        return ""
