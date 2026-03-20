import google.generativeai as genai
import json
import time
from os import getenv
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

GEMINI_API_KEY = getenv("GEMINI_API_KEY")

class VeriNewsVerifier:
    def __init__(self):
        if GEMINI_API_KEY and isinstance(GEMINI_API_KEY, str):
            print(f"DEBUG: GEMINI_API_KEY starts with {GEMINI_API_KEY[:5]}...")
            genai.configure(api_key=GEMINI_API_KEY)
            self.model_name = 'models/gemini-2.0-flash'
            self.safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=[{'google_search_retrieval': {}}],
                safety_settings=self.safety_settings
            )
        else:
            self.model = None
            logger.error("GEMINI_API_KEY not found. Verifier service unavailable.")

    def verify_content(self, text: str, detailed: bool = False, retries: int = 2) -> dict:
        """
        Performs a unified check for fake news detection, scoring, and explanation.
        """
        if not self.model:
            return {
                "result": "Uncertain",
                "score": 50,
                "confidence": "Low",
                "contradictions": [],
                "explanation": "Service unavailable. Please check API configuration."
            }

        prompt_length = "4–5 lines" if detailed else "2–3 lines"
        current_date = time.strftime("%Y-%m-%d")
        prompt = f"""
You are an AI system for fake news detection and verification. 
Current Date: {current_date}

Analyze the following news content and return a structured response.

Tasks:
1. Classify the content as "Fake" or "Real"
2. Provide a confidence score between 0 and 100
3. Assign a confidence level:
   - 80-100: High
   - 50-79: Medium
   - 0-49: Low

    - DO NOT make up unknown facts

5. Give a {prompt_length} explanation focusing on:
   - tone and emotional language
   - credibility of claims
   - exaggeration or bias

6. Provide 4–6 CITATIONS & REFERENCES:
   - These should be credible sources that would have information on this topic
   - Format: "Source Name - Period/Edition" (e.g., "Reuters Archive - 2026 Edition")
   - Do not include URLs, just the source name and context.
   - Use a mix of historical and modern-sounding institutions.

IMPORTANT:
- Do NOT hallucinate
- If factual contradiction is uncertain, return empty list
- Be conservative and accurate

Return ONLY valid JSON in this format:
{{
  "result": "Fake or Real",
  "score": number,
  "confidence": "High/Medium/Low",
  "contradictions": ["point1", "point2", "point3"],
  "explanation": "string",
  "citations": [
    {{"source": "Reuters Archive", "context": "2026 Edition"}},
    {{"source": "Bombay Times", "context": "Vol. 42-B"}}
  ]
}}

Content:
{str(text)[:3000]}
"""

        for attempt in range(retries + 1):
            try:
                # Try futuristic models available in this 2026 environment
                models_to_try = [
                    'models/gemini-2.5-flash-lite-preview',
                    'models/gemini-3.1-flash-lite-preview',
                    'models/gemini-2.1-flash-thinking-exp',
                    'models/gemini-1.5-flash-latest'
                ]
                
                # We will try each model WITH tools first, then WITHOUT tools as a last resort
                for with_tools in [True, False]:
                    for model_name in models_to_try:
                        try:
                            # Skip grounding for some experimental models if needed, but trying all first
                            logger.info(f"Attempting verification", model=model_name, ground=with_tools, attempt=attempt+1)
                            
                            tools = [{'google_search_retrieval': {}}] if with_tools else None
                            
                            m = genai.GenerativeModel(
                                model_name=model_name,
                                tools=tools,
                                safety_settings=self.safety_settings
                            )
                            response = m.generate_content(prompt)
                            
                            if not response or not response.candidates:
                                with open("verifier_error.log", "a", encoding="utf-8") as ef:
                                    ef.write(f"  EMPTY response from {model_name} (ground={with_tools})\n")
                                continue

                            # Extract text robustly
                            raw_text = ""
                            try:
                                # First try standard attribute
                                if hasattr(response, 'text'):
                                    raw_text = response.text
                                elif response.candidates and response.candidates[0].content.parts:
                                    raw_text = "".join([p.text for p in response.candidates[0].content.parts if hasattr(p, 'text')])
                            except (AttributeError, ValueError):
                                # Secondary fallback to candidates list
                                if response.candidates and response.candidates[0].content.parts:
                                    raw_text = "".join([p.text for p in response.candidates[0].content.parts if hasattr(p, 'text')])
                            
                            if raw_text and isinstance(raw_text, str):
                                clean_res = raw_text.strip().replace('```json', '').replace('```', '')
                                start_idx = clean_res.find('{')
                                end_idx = clean_res.rfind('}')
                                if start_idx != -1 and end_idx != -1:
                                    # Perform slice safely
                                    clean_res = clean_res[int(start_idx):int(end_idx)+1]
                                
                                result = json.loads(clean_res)
                                expected_keys = ["result", "score", "confidence", "contradictions", "explanation", "citations"]
                                if all(key in result for key in expected_keys):
                                    logger.info(f"Verification SUCCESS", model=model_name, ground=with_tools)
                                    return result
                            
                        except Exception as mod_e:
                            with open("verifier_error.log", "a", encoding="utf-8") as ef:
                                ef.write(f"  FAILED {model_name} (ground={with_tools}): {str(mod_e)}\n")
                            logger.warning(f"Model {model_name} (ground={with_tools}) failed: {str(mod_e)}")
                            continue
                
                raise ValueError("All models and tool configurations failed.")
                    
                raise ValueError("Incomplete response from AI")

            except Exception as e:
                import traceback
                error_msg = f"Verification attempt failed: {str(e)}"
                print(error_msg) # Direct console output for quick debug
                
                # EMERGENCY LOG FILE
                with open("verifier_error.log", "a", encoding="utf-8") as ef:
                    ef.write(f"\n--- ATTEMPT {attempt+1} ---\n")
                    ef.write(error_msg + "\n")
                    ef.write(traceback.format_exc() + "\n")

                logger.error(error_msg, 
                             attempt=attempt+1, 
                             error=str(e),
                             traceback=traceback.format_exc())
                if attempt == retries:
                    return {
                        "result": "Uncertain",
                        "score": 50,
                        "confidence": "Low",
                        "contradictions": [],
                        "explanation": f"The analysis failed after {retries+1} attempts. Please try again later.",
                        "citations": []
                    }
            time.sleep(1)

        return {
            "result": "Uncertain",
            "score": 50,
            "confidence": "Low",
            "contradictions": [],
            "explanation": "No response could be obtained from the AI models after multiple attempts.",
            "citations": []
        }

# Global Instance
verifier = VeriNewsVerifier()
