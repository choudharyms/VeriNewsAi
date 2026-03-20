from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List
import time
from utils.logger import logger
from utils.cleaner import clean_text, get_keyword_score, get_cache_key
from services.scraper import extract_article
from services.verifier import verifier

router = APIRouter()

# In-memory cache
ANALYSIS_CACHE = {}

class AnalysisRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    detailed: bool = False

class AnalysisResponse(BaseModel):
    result: str
    score: int
    confidence: str
    contradictions: List[str]
    explanation: str
    citations: List[dict]
    source: str
    processing_time_ms: int

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_news(req: AnalysisRequest):
    start_time = time.time()
    
    # 1. Input Logic
    source_type = "text"
    content = ""
    
    if req.url:
        source_type = "url"
        content = extract_article(req.url)
        if not content:
            raise HTTPException(
                status_code=400, 
                detail="This site blocks automated extraction. Paste the article for best results."
            )
    elif req.text:
        source_type = "text"
        content = req.text
    else:
        raise HTTPException(status_code=400, detail="Either 'text' or 'url' must be provided.")

    # 2. Text Processing
    cleaned_content = clean_text(content)
    if len(cleaned_content.strip()) < 50:
        raise HTTPException(status_code=422, detail="Content too short for meaningful analysis (min 50 chars).")

    # 3. Caching
    cache_key = get_cache_key(cleaned_content + str(req.detailed))
    if cache_key in ANALYSIS_CACHE:
        logger.info("Returning cached result", cache_key=cache_key)
        cached_res = ANALYSIS_CACHE[cache_key].copy()
        cached_res["processing_time_ms"] = int((time.time() - start_time) * 1000)
        return cached_res

    try:
        # 4. Unified AI Verification
        # Gemini provides result, score, confidence, contradictions, and explanation in one call.
        verification = verifier.verify_content(cleaned_content, detailed=req.detailed)
        logger.info("Raw AI Verification", analysis=verification)
        
        # 5. Hybrid Scoring Adjustment
        # If the AI failed or is uncertain, don't try to normalize the score.
        if verification.get('result') == "Uncertain":
            ai_score = 50
            final_result = "Uncertain"
            final_score = 50
        else:
            # Normalize Gemini's score so higher always means "More Suspicious/Fake"
            raw_ai_score = verification.get('score', 50)
            if verification.get('result', '').lower() == "real":
                ai_score = 100 - raw_ai_score
            else:
                ai_score = raw_ai_score

            keyword_score = get_keyword_score(cleaned_content)
            final_score = int((0.7 * ai_score) + (0.3 * keyword_score))
            final_result = "Fake" if final_score > 50 else "Real"
        
        if final_score >= 80:
            final_confidence = "High"
        elif final_score >= 50:
            final_confidence = "Medium"
        else:
            final_confidence = "Low"

        processing_time_ms = int((time.time() - start_time) * 1000)
        
        response_data = {
            "result": final_result,
            "score": final_score,
            "confidence": final_confidence,
            "contradictions": verification['contradictions'],
            "explanation": verification['explanation'],
            "citations": verification.get('citations', []),
            "source": source_type,
            "processing_time_ms": processing_time_ms
        }

        # Cache result
        ANALYSIS_CACHE[cache_key] = response_data
        
        logger.info("Analysis complete", 
                    final_score=final_score, 
                    result=final_result, 
                    processing_time=processing_time_ms)
        
        return response_data

    except Exception as e:
        logger.error("Analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="An internal error occurred during analysis.")
