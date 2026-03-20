# VeriNewsAI - AI-Powered Fake News Detection System

A production-ready FastAPI backend for detecting fake news using Hugging Face's BERT model and Google Gemini for explanations.

## Features
- **URL Extraction**: Automatically extracts article content from URLs using `newspaper3k`.
- **Hybrid Scoring**: Uses a blend of AI model predictions (70%) and keyword-based suspicion (30%).
- **Fallback Mechanism**: Reliable keyword-based scoring if AI services are unavailable.
- **LLM Explainer**: Detailed or brief explanations powered by Gemini 1.5 Flash.
- **Performance**: In-memory caching and startup model warm-up.
- **Robustness**: 10s timeouts, retries, and structured logging.

## Tech Stack
- Python 3.9+
- FastAPI
- Hugging Face Inference API
- Google Gemini API
- Pydantic
- Newspaper3k

## Getting Started

1. **Clone and Setup**:
   ```bash
   git clone <repo-url>
   cd VeriNewsAI
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file based on `.env.example`:
   ```env
   HF_API_KEY=your_huggingface_key
   GEMINI_API_KEY=your_gemini_key
   ```

3. **Run the Server**:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`.

## API Endpoints

### 1. Health Check
- **URL**: `GET /health`
- **Response**: `{"status": "ok"}`

### 2. Analyze News
- **URL**: `POST /analyze`
- **Body**:
  ```json
  {
    "url": "https://example.com/article",
    "detailed": true
  }
  ```
- **Response**:
  ```json
  {
    "result": "Fake",
    "score": 85,
    "confidence": "High",
    "explanation": "...",
    "source": "url",
    "processing_time_ms": 1240
  }
  ```

## Project Structure
- `main.py`: Entry point and server configuration.
- `routes/`: API endpoint definitions.
- `services/`: Scraper, Detector, and Explainer logic.
- `utils/`: Logging, text cleaning, and caching utilities.
